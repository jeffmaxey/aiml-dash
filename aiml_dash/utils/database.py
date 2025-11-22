"""
Database Connection Manager
============================

Manages SQL database connections with pooling support.
Provides utilities for connecting to databases using pyodbc, sqlalchemy, and pandas.
"""

from __future__ import annotations

from collections.abc import Callable
from contextlib import contextmanager
from typing import TYPE_CHECKING
from urllib.parse import quote_plus

import pandas as pd

from aiml_dash.utils.logging import get_logger

if TYPE_CHECKING:
    import pyodbc
    import sqlalchemy

logger = get_logger(__name__)


class DatabaseManager:
    """
    Manages database connections with connection pooling.

    Supports multiple database types including SQL Server, PostgreSQL,
    MySQL, SQLite, and any ODBC-compliant database.
    """

    def __init__(self):
        """Initialize the database manager."""
        self._connections: dict[str, dict] = {}
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
        """
        Add a database connection configuration.

        Parameters
        ----------
        name : str
            Connection name
        connection_string : str, optional
            Full connection string
        driver : str, optional
            Database driver (e.g., 'ODBC Driver 17 for SQL Server')
        server : str, optional
            Server hostname or IP
        database : str, optional
            Database name
        username : str, optional
            Username for authentication
        password : str, optional
            Password for authentication
        port : int, optional
            Port number
        dialect : str
            SQLAlchemy dialect (mssql, postgresql, mysql, sqlite)
        use_sqlalchemy : bool
            Whether to use SQLAlchemy engine
        """
        if connection_string is None:
            # Build connection string
            if dialect == "mssql":
                if driver is None:
                    driver = "ODBC Driver 17 for SQL Server"

                conn_parts = [f"DRIVER={{{driver}}}", f"SERVER={server}"]

                if port:
                    conn_parts[-1] += f",{port}"

                conn_parts.append(f"DATABASE={database}")

                if username and password:
                    conn_parts.extend([f"UID={username}", f"PWD={password}"])
                else:
                    conn_parts.append("Trusted_Connection=yes")

                connection_string = ";".join(conn_parts)

            elif dialect == "postgresql":
                driver = driver or "postgresql+psycopg2"
                port = port or 5432
                connection_string = f"{driver}://{username}:{password}@{server}:{port}/{database}"

            elif dialect == "mysql":
                driver = driver or "mysql+pymysql"
                port = port or 3306
                connection_string = f"{driver}://{username}:{password}@{server}:{port}/{database}"

            elif dialect == "sqlite":
                connection_string = f"sqlite:///{database}"

        self._connections[name] = {
            "connection_string": connection_string,
            "dialect": dialect,
            "use_sqlalchemy": use_sqlalchemy,
            "driver": driver,
            "server": server,
            "database": database,
        }

        logger.info(f"Added database connection: {name} ({dialect})")

    def get_connection(self, name: str) -> pyodbc.Connection:
        """
        Get a raw pyodbc connection.

        Parameters
        ----------
        name : str
            Connection name

        Returns
        -------
        pyodbc.Connection
            Database connection
        """
        try:
            import pyodbc
        except ImportError as e:
            raise ImportError("pyodbc is required for database connections") from e

        if name not in self._connections:
            raise ValueError(f"Connection '{name}' not found")

        config = self._connections[name]
        conn = pyodbc.connect(config["connection_string"])
        logger.debug(f"Opened connection: {name}")
        return conn

    def get_engine(self, name: str) -> sqlalchemy.Engine:
        """
        Get or create a SQLAlchemy engine with connection pooling.

        Parameters
        ----------
        name : str
            Connection name

        Returns
        -------
        sqlalchemy.Engine
            SQLAlchemy engine
        """
        try:
            from sqlalchemy import create_engine
        except ImportError as e:
            raise ImportError("sqlalchemy is required for engine support") from e

        if name in self._engines:
            return self._engines[name]

        if name not in self._connections:
            raise ValueError(f"Connection '{name}' not found")

        config = self._connections[name]

        # Build SQLAlchemy connection string
        if config["dialect"] == "mssql":
            # URL encode the connection string for SQLAlchemy
            params = quote_plus(config["connection_string"])
            conn_str = f"mssql+pyodbc:///?odbc_connect={params}"
        else:
            conn_str = config["connection_string"]

        engine = create_engine(
            conn_str,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=3600,
        )

        self._engines[name] = engine
        logger.info(f"Created SQLAlchemy engine: {name}")
        return engine

    @contextmanager
    def connection_context(self, name: str):
        """
        Context manager for database connections.

        Parameters
        ----------
        name : str
            Connection name

        Yields
        ------
        pyodbc.Connection
            Database connection
        """
        conn = self.get_connection(name)
        try:
            yield conn
        finally:
            conn.close()
            logger.debug(f"Closed connection: {name}")

    def query_dataframe(
        self,
        name: str,
        query: str,
        params: dict | None = None,
        use_engine: bool = True,
    ) -> pd.DataFrame:
        """
        Execute a query and return results as a DataFrame.

        Parameters
        ----------
        name : str
            Connection name
        query : str
            SQL query
        params : dict, optional
            Query parameters
        use_engine : bool
            Use SQLAlchemy engine if available

        Returns
        -------
        pd.DataFrame
            Query results
        """
        logger.debug(f"Executing query on {name}: {query[:100]}...")

        if use_engine and self._connections[name].get("use_sqlalchemy", True):
            engine = self.get_engine(name)
            df = pd.read_sql(query, engine, params=params)
        else:
            with self.connection_context(name) as conn:
                df = pd.read_sql(query, conn, params=params)

        logger.info(f"Query returned {len(df)} rows")
        return df

    def execute_query(
        self,
        name: str,
        query: str,
        params: dict | None = None,
        commit: bool = True,
    ) -> int:
        """
        Execute a non-SELECT query (INSERT, UPDATE, DELETE, etc.).

        Parameters
        ----------
        name : str
            Connection name
        query : str
            SQL query
        params : dict, optional
            Query parameters
        commit : bool
            Whether to commit the transaction

        Returns
        -------
        int
            Number of affected rows
        """
        logger.debug(f"Executing non-SELECT query on {name}")

        with self.connection_context(name) as conn:
            cursor = conn.cursor()

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            rowcount = cursor.rowcount

            if commit:
                conn.commit()

            cursor.close()

        logger.info(f"Query affected {rowcount} rows")
        return rowcount

    def get_tables(self, name: str, schema: str | None = None) -> list[str]:
        """
        Get list of tables in the database.

        Parameters
        ----------
        name : str
            Connection name
        schema : str, optional
            Schema name (database-specific)

        Returns
        -------
        list of str
            Table names
        """
        config = self._connections[name]
        dialect = config["dialect"]

        if dialect == "mssql":
            query = """
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
            """
            if schema:
                query += f" AND TABLE_SCHEMA = '{schema}'"

        elif dialect in ["postgresql", "mysql"]:
            query = """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_type = 'BASE TABLE'
            """
            if schema:
                query += f" AND table_schema = '{schema}'"

        elif dialect == "sqlite":
            query = "SELECT name FROM sqlite_master WHERE type='table'"

        else:
            raise ValueError(f"Unsupported dialect: {dialect}")

        df = self.query_dataframe(name, query)
        return df.iloc[:, 0].tolist()

    def get_columns(self, name: str, table: str, schema: str | None = None) -> pd.DataFrame:
        """
        Get column information for a table.

        Parameters
        ----------
        name : str
            Connection name
        table : str
            Table name
        schema : str, optional
            Schema name

        Returns
        -------
        pd.DataFrame
            Column information (name, type, nullable, etc.)
        """
        config = self._connections[name]
        dialect = config["dialect"]

        if dialect == "mssql":
            query = f"""
                SELECT 
                    COLUMN_NAME, 
                    DATA_TYPE, 
                    IS_NULLABLE,
                    CHARACTER_MAXIMUM_LENGTH
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = '{table}'
            """
            if schema:
                query += f" AND TABLE_SCHEMA = '{schema}'"

        elif dialect in ["postgresql", "mysql"]:
            query = f"""
                SELECT 
                    column_name, 
                    data_type, 
                    is_nullable,
                    character_maximum_length
                FROM information_schema.columns 
                WHERE table_name = '{table}'
            """
            if schema:
                query += f" AND table_schema = '{schema}'"

        else:
            raise ValueError(f"Unsupported dialect: {dialect}")

        return self.query_dataframe(name, query)

    def list_connections(self) -> list[str]:
        """Get list of configured connection names."""
        return list(self._connections.keys())

    def remove_connection(self, name: str) -> None:
        """Remove a connection configuration."""
        if name in self._connections:
            del self._connections[name]

        if name in self._engines:
            self._engines[name].dispose()
            del self._engines[name]

        logger.info(f"Removed connection: {name}")


# Global database manager instance
db_manager = DatabaseManager()

__all__ = ["DatabaseManager", "db_manager"]
