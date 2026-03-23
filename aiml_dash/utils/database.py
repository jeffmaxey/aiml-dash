"""Database connection management for AIML Dash."""

from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, Any
from urllib.parse import quote_plus

import pandas as pd

from aiml_dash.utils.logging import get_logger

if TYPE_CHECKING:
    import pyodbc
    import sqlalchemy

logger = get_logger(__name__)

READ_ONLY_PREFIXES = ("select", "with", "pragma", "show", "describe", "explain")


class DatabaseManager:
    """Manage database connections with conservative query validation."""

    def __init__(self):
        """Initialize the database manager."""
        self._connections: dict[str, dict[str, Any]] = {}
        self._engines: dict[str, sqlalchemy.Engine] = {}

    def add_connection(
        self,
        name: str,
        connection_string: str | None = None,
        driver: str | None = None,
        server: str | None = None,
        database: str | None = None,
        username: str | None = None,
        password: str | None = None,
        port: int | None = None,
        dialect: str = "mssql",
        use_sqlalchemy: bool = True,
    ) -> None:
        """Register a connection configuration."""
        if connection_string is None:
            connection_string = self._build_connection_string(
                driver=driver,
                server=server,
                database=database,
                username=username,
                password=password,
                port=port,
                dialect=dialect,
            )

        self._connections[name] = {
            "connection_string": connection_string,
            "dialect": dialect,
            "use_sqlalchemy": use_sqlalchemy,
            "driver": driver,
            "server": server,
            "database": database,
        }
        logger.info("Registered database connection '%s' (%s)", name, dialect)

    def _build_connection_string(
        self,
        *,
        driver: str | None,
        server: str | None,
        database: str | None,
        username: str | None,
        password: str | None,
        port: int | None,
        dialect: str,
    ) -> str:
        """Build a connection string for the requested dialect."""
        if dialect == "mssql":
            resolved_driver = driver or "ODBC Driver 17 for SQL Server"
            conn_parts = [f"DRIVER={{{resolved_driver}}}", f"SERVER={server}"]
            if port:
                conn_parts[-1] += f",{port}"
            conn_parts.append(f"DATABASE={database}")
            if username and password:
                conn_parts.extend([f"UID={username}", f"PWD={password}"])
            else:
                conn_parts.append("Trusted_Connection=yes")
            return ";".join(conn_parts)
        if dialect == "postgresql":
            resolved_driver = driver or "postgresql+psycopg2"
            resolved_port = port or 5432
            return f"{resolved_driver}://{username}:{password}@{server}:{resolved_port}/{database}"
        if dialect == "mysql":
            resolved_driver = driver or "mysql+pymysql"
            resolved_port = port or 3306
            return f"{resolved_driver}://{username}:{password}@{server}:{resolved_port}/{database}"
        if dialect == "sqlite":
            return f"sqlite:///{database}"
        raise ValueError(f"Unsupported dialect: {dialect}")

    def _get_connection_config(self, name: str) -> dict[str, Any]:
        """Return connection config or raise a clear error."""
        if name not in self._connections:
            raise ValueError(f"Connection '{name}' not found")
        return self._connections[name]

    def _validate_query(self, query: str, *, allow_write: bool) -> None:
        """Reject obviously unsafe or unexpected SQL."""
        normalized = " ".join(query.strip().split()).lower()
        if not normalized:
            raise ValueError("Query must not be empty")
        if not allow_write and not normalized.startswith(READ_ONLY_PREFIXES):
            raise ValueError("Only read-only queries are allowed by this method")
        if ";" in normalized.rstrip(";"):
            raise ValueError("Multiple SQL statements are not allowed")

    def get_connection(self, name: str) -> pyodbc.Connection:
        """Return a raw pyodbc connection."""
        try:
            import pyodbc
        except ImportError as exc:
            raise ImportError("pyodbc is required for database connections") from exc

        config = self._get_connection_config(name)
        conn = pyodbc.connect(config["connection_string"])
        logger.debug("Opened raw connection '%s'", name)
        return conn

    def get_engine(self, name: str) -> sqlalchemy.Engine:
        """Return a SQLAlchemy engine for a registered connection."""
        try:
            from sqlalchemy import create_engine
        except ImportError as exc:
            raise ImportError("sqlalchemy is required for engine support") from exc

        if name in self._engines:
            return self._engines[name]

        config = self._get_connection_config(name)
        if config["dialect"] == "mssql":
            params = quote_plus(config["connection_string"])
            connection_string = f"mssql+pyodbc:///?odbc_connect={params}"
        else:
            connection_string = config["connection_string"]

        engine = create_engine(
            connection_string,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args={"timeout": 30} if config["dialect"] != "sqlite" else {},
        )
        self._engines[name] = engine
        logger.info("Created SQLAlchemy engine '%s'", name)
        return engine

    @contextmanager
    def connection_context(self, name: str):
        """Yield a raw connection and ensure it closes."""
        conn = self.get_connection(name)
        try:
            yield conn
        finally:
            conn.close()
            logger.debug("Closed raw connection '%s'", name)

    def query_dataframe(
        self,
        name: str,
        query: str,
        params: dict[str, Any] | None = None,
        use_engine: bool = True,
    ) -> pd.DataFrame:
        """Execute a read-only query and return a DataFrame."""
        self._validate_query(query, allow_write=False)
        logger.debug("Executing read query on '%s'", name)

        config = self._get_connection_config(name)
        if use_engine and config.get("use_sqlalchemy", True):
            engine = self.get_engine(name)
            return pd.read_sql(query, engine, params=params)

        with self.connection_context(name) as conn:
            return pd.read_sql(query, conn, params=params)

    def execute_query(
        self,
        name: str,
        query: str,
        params: dict[str, Any] | tuple[Any, ...] | None = None,
        commit: bool = True,
    ) -> int:
        """Execute a write query and return affected row count."""
        self._validate_query(query, allow_write=True)
        logger.debug("Executing write query on '%s'", name)

        with self.connection_context(name) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            rowcount = cursor.rowcount
            if commit:
                conn.commit()
            cursor.close()
        logger.info("Write query on '%s' affected %s rows", name, rowcount)
        return rowcount

    def get_tables(self, name: str, schema: str | None = None) -> list[str]:
        """Return available tables for a connection."""
        config = self._get_connection_config(name)
        dialect = config["dialect"]

        if dialect == "mssql":
            query = """
                SELECT TABLE_NAME
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_TYPE = 'BASE TABLE'
            """
            params = {"schema": schema} if schema else None
            if schema:
                query += " AND TABLE_SCHEMA = :schema"
        elif dialect in {"postgresql", "mysql"}:
            query = """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_type = 'BASE TABLE'
            """
            params = {"schema": schema} if schema else None
            if schema:
                query += " AND table_schema = :schema"
        elif dialect == "sqlite":
            query = "SELECT name FROM sqlite_master WHERE type='table'"
            params = None
        else:
            raise ValueError(f"Unsupported dialect: {dialect}")

        df = self.query_dataframe(name, query, params=params)
        return df.iloc[:, 0].tolist()

    def get_columns(
        self, name: str, table: str, schema: str | None = None
    ) -> pd.DataFrame:
        """Return column metadata for a table."""
        if not table.replace("_", "").isalnum():
            raise ValueError("Table name contains unsupported characters")
        if schema and not schema.replace("_", "").isalnum():
            raise ValueError("Schema name contains unsupported characters")

        config = self._get_connection_config(name)
        dialect = config["dialect"]

        if dialect == "mssql":
            query = """
                SELECT
                    COLUMN_NAME,
                    DATA_TYPE,
                    IS_NULLABLE,
                    CHARACTER_MAXIMUM_LENGTH
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = :table
            """
            params: dict[str, Any] = {"table": table}
            if schema:
                query += " AND TABLE_SCHEMA = :schema"
                params["schema"] = schema
        elif dialect in {"postgresql", "mysql"}:
            query = """
                SELECT
                    column_name,
                    data_type,
                    is_nullable,
                    character_maximum_length
                FROM information_schema.columns
                WHERE table_name = :table
            """
            params = {"table": table}
            if schema:
                query += " AND table_schema = :schema"
                params["schema"] = schema
        else:
            raise ValueError(f"Unsupported dialect: {dialect}")

        return self.query_dataframe(name, query, params=params)

    def list_connections(self) -> list[str]:
        """Return configured connection names."""
        return list(self._connections.keys())

    def remove_connection(self, name: str) -> None:
        """Remove a registered connection."""
        self._connections.pop(name, None)
        if name in self._engines:
            self._engines[name].dispose()
            del self._engines[name]
        logger.info("Removed database connection '%s'", name)


db_manager = DatabaseManager()

__all__ = ["DatabaseManager", "db_manager"]

