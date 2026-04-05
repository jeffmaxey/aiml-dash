"""Tests for aiml_dash.utils.database module.

Covers DatabaseManager construction, _build_connection_string,
_validate_query, add_connection, list_connections, remove_connection,
_get_connection_config, get_columns, and get_tables routing logic.
Real network connections are never opened.
"""

from __future__ import annotations

from contextlib import contextmanager
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from aiml_dash.utils.database import DatabaseManager, READ_ONLY_PREFIXES


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def db():
    """Return a fresh DatabaseManager for each test."""
    return DatabaseManager()


# ---------------------------------------------------------------------------
# DatabaseManager initialisation
# ---------------------------------------------------------------------------


class TestDatabaseManagerInit:
    """Tests for DatabaseManager.__init__."""

    def test_connections_dict_empty_on_creation(self, db):
        """Newly created manager should have no registered connections."""
        assert db._connections == {}

    def test_engines_dict_empty_on_creation(self, db):
        """Newly created manager should have no cached engines."""
        assert db._engines == {}


# ---------------------------------------------------------------------------
# _build_connection_string
# ---------------------------------------------------------------------------


class TestBuildConnectionString:
    """Tests for DatabaseManager._build_connection_string."""

    def test_mssql_trusted(self, db):
        """MSSQL with no credentials should produce a Trusted_Connection string."""
        cs = db._build_connection_string(
            driver=None,
            server="myserver",
            database="mydb",
            username=None,
            password=None,
            port=None,
            dialect="mssql",
        )
        assert "myserver" in cs
        assert "mydb" in cs
        assert "Trusted_Connection=yes" in cs

    def test_mssql_with_credentials(self, db):
        """MSSQL with credentials should embed UID/PWD."""
        cs = db._build_connection_string(
            driver=None,
            server="srv",
            database="db",
            username="user",
            password="pass",
            port=None,
            dialect="mssql",
        )
        assert "UID=user" in cs
        assert "PWD=pass" in cs

    def test_mssql_custom_port(self, db):
        """MSSQL port should appear after the server name."""
        cs = db._build_connection_string(
            driver=None,
            server="srv",
            database="db",
            username=None,
            password=None,
            port=1433,
            dialect="mssql",
        )
        assert "1433" in cs

    def test_postgresql(self, db):
        """PostgreSQL connection string should contain the host and database."""
        cs = db._build_connection_string(
            driver=None,
            server="pghost",
            database="pgdb",
            username="pguser",
            password="pgpass",
            port=5432,
            dialect="postgresql",
        )
        assert "pghost" in cs
        assert "pgdb" in cs
        assert "5432" in cs

    def test_mysql(self, db):
        """MySQL connection string should contain the host and database."""
        cs = db._build_connection_string(
            driver=None,
            server="mysqlhost",
            database="mysqldb",
            username="root",
            password="secret",
            port=3306,
            dialect="mysql",
        )
        assert "mysqlhost" in cs
        assert "mysqldb" in cs

    def test_sqlite(self, db):
        """SQLite connection string should be a file URI."""
        cs = db._build_connection_string(
            driver=None,
            server=None,
            database="/tmp/test.db",
            username=None,
            password=None,
            port=None,
            dialect="sqlite",
        )
        assert "sqlite:///" in cs
        assert "test.db" in cs

    def test_unsupported_dialect_raises(self, db):
        """An unsupported dialect should raise ValueError."""
        with pytest.raises(ValueError, match="Unsupported dialect"):
            db._build_connection_string(
                driver=None,
                server=None,
                database=None,
                username=None,
                password=None,
                port=None,
                dialect="oracle",
            )

    def test_mssql_default_driver_used(self, db):
        """MSSQL should use the default ODBC driver when none is specified."""
        cs = db._build_connection_string(
            driver=None,
            server="s",
            database="d",
            username=None,
            password=None,
            port=None,
            dialect="mssql",
        )
        assert "ODBC Driver 17 for SQL Server" in cs

    def test_postgresql_default_port(self, db):
        """PostgreSQL should use port 5432 by default."""
        cs = db._build_connection_string(
            driver=None,
            server="s",
            database="d",
            username="u",
            password="p",
            port=None,
            dialect="postgresql",
        )
        assert "5432" in cs

    def test_mysql_default_port(self, db):
        """MySQL should use port 3306 by default."""
        cs = db._build_connection_string(
            driver=None,
            server="s",
            database="d",
            username="u",
            password="p",
            port=None,
            dialect="mysql",
        )
        assert "3306" in cs


# ---------------------------------------------------------------------------
# add_connection / list_connections / remove_connection
# ---------------------------------------------------------------------------


class TestConnectionManagement:
    """Tests for add_connection, list_connections, and remove_connection."""

    def test_add_connection_stores_config(self, db):
        """add_connection() should persist the connection configuration."""
        db.add_connection(
            "myconn",
            connection_string="sqlite:///test.db",
            dialect="sqlite",
        )
        assert "myconn" in db._connections

    def test_list_connections_empty_by_default(self, db):
        """list_connections() should return an empty list for a fresh manager."""
        assert db.list_connections() == []

    def test_list_connections_returns_names(self, db):
        """list_connections() should return all registered connection names."""
        db.add_connection("a", connection_string="sqlite:///a.db")
        db.add_connection("b", connection_string="sqlite:///b.db")
        names = db.list_connections()
        assert set(names) == {"a", "b"}

    def test_remove_connection_removes_entry(self, db):
        """remove_connection() should delete the named connection."""
        db.add_connection("tmp", connection_string="sqlite:///tmp.db")
        db.remove_connection("tmp")
        assert "tmp" not in db._connections

    def test_remove_connection_no_error_if_missing(self, db):
        """remove_connection() should not raise when the name does not exist."""
        db.remove_connection("nonexistent")  # must not raise

    def test_remove_connection_disposes_engine(self, db):
        """remove_connection() should call dispose() on a cached engine."""
        db.add_connection("eng", connection_string="sqlite:///eng.db")
        mock_engine = MagicMock()
        db._engines["eng"] = mock_engine
        db.remove_connection("eng")
        mock_engine.dispose.assert_called_once()
        assert "eng" not in db._engines

    def test_add_connection_builds_string_when_none(self, db):
        """add_connection() should auto-build a connection string if none given."""
        db.add_connection(
            "autoconn",
            server="srv",
            database="testdb",
            dialect="sqlite",
        )
        assert "autoconn" in db._connections

    def test_add_connection_stores_dialect(self, db):
        """add_connection() should store the dialect in the config."""
        db.add_connection("dlconn", connection_string="sqlite:///x.db", dialect="sqlite")
        assert db._connections["dlconn"]["dialect"] == "sqlite"


# ---------------------------------------------------------------------------
# _get_connection_config
# ---------------------------------------------------------------------------


class TestGetConnectionConfig:
    """Tests for DatabaseManager._get_connection_config."""

    def test_returns_config_for_known_connection(self, db):
        """_get_connection_config() should return the stored config dict."""
        db.add_connection("known", connection_string="sqlite:///x.db")
        config = db._get_connection_config("known")
        assert isinstance(config, dict)
        assert "connection_string" in config

    def test_raises_for_unknown_connection(self, db):
        """_get_connection_config() should raise ValueError for unknown names."""
        with pytest.raises(ValueError, match="not found"):
            db._get_connection_config("unknown")


# ---------------------------------------------------------------------------
# _validate_query
# ---------------------------------------------------------------------------


class TestValidateQuery:
    """Tests for DatabaseManager._validate_query."""

    def test_select_allowed_in_readonly(self, db):
        """SELECT queries should pass read-only validation."""
        db._validate_query("SELECT * FROM t", allow_write=False)  # no exception

    def test_with_clause_allowed_in_readonly(self, db):
        """WITH (CTE) queries should pass read-only validation."""
        db._validate_query("WITH cte AS (SELECT 1) SELECT * FROM cte", allow_write=False)

    def test_insert_blocked_in_readonly(self, db):
        """INSERT should be blocked in read-only mode."""
        with pytest.raises(ValueError, match="read-only"):
            db._validate_query("INSERT INTO t VALUES (1)", allow_write=False)

    def test_insert_allowed_in_write_mode(self, db):
        """INSERT should pass when allow_write=True."""
        db._validate_query("INSERT INTO t VALUES (1)", allow_write=True)

    def test_empty_query_raises(self, db):
        """An empty query should raise ValueError."""
        with pytest.raises(ValueError, match="not be empty"):
            db._validate_query("", allow_write=False)

    def test_whitespace_only_raises(self, db):
        """A whitespace-only query should raise ValueError."""
        with pytest.raises(ValueError, match="not be empty"):
            db._validate_query("   ", allow_write=False)

    def test_multiple_statements_blocked(self, db):
        """Multiple SQL statements (semicolon separator) should be blocked."""
        with pytest.raises(ValueError, match="Multiple SQL statements"):
            db._validate_query("SELECT 1; DROP TABLE t", allow_write=False)

    def test_trailing_semicolon_allowed(self, db):
        """A single trailing semicolon should not trigger multi-statement error."""
        db._validate_query("SELECT 1;", allow_write=False)  # no exception

    def test_show_allowed_in_readonly(self, db):
        """SHOW queries should pass read-only validation."""
        db._validate_query("SHOW TABLES", allow_write=False)

    def test_pragma_allowed_in_readonly(self, db):
        """PRAGMA queries should pass read-only validation."""
        db._validate_query("PRAGMA table_info(t)", allow_write=False)


# ---------------------------------------------------------------------------
# READ_ONLY_PREFIXES constant
# ---------------------------------------------------------------------------


class TestReadOnlyPrefixes:
    """Tests for the READ_ONLY_PREFIXES constant."""

    def test_is_tuple(self):
        """READ_ONLY_PREFIXES should be a tuple."""
        assert isinstance(READ_ONLY_PREFIXES, tuple)

    def test_contains_select(self):
        """READ_ONLY_PREFIXES should include 'select'."""
        assert "select" in READ_ONLY_PREFIXES

    def test_all_lowercase(self):
        """All prefixes should be lowercase for case-insensitive comparison."""
        for prefix in READ_ONLY_PREFIXES:
            assert prefix == prefix.lower()


# ---------------------------------------------------------------------------
# get_tables dialect routing (logic only; no real DB)
# ---------------------------------------------------------------------------


class TestGetTablesRouting:
    """Tests for get_tables() dialect-specific query selection."""

    def _db_with_mock_query(self, dialect: str):
        """Return a manager wired to capture the SQL sent to query_dataframe."""
        db = DatabaseManager()
        db.add_connection("conn", connection_string="sqlite:///x.db", dialect=dialect)
        return db

    def test_sqlite_get_tables_uses_sqlite_master(self):
        """get_tables() for SQLite should query sqlite_master."""
        db = self._db_with_mock_query("sqlite")
        captured = {}

        def fake_query(name, query, params=None):
            captured["query"] = query
            return pd.DataFrame({"name": []})

        with patch.object(db, "query_dataframe", side_effect=fake_query):
            db.get_tables("conn")

        assert "sqlite_master" in captured["query"]

    def test_mssql_get_tables_uses_information_schema(self):
        """get_tables() for MSSQL should query INFORMATION_SCHEMA."""
        db = self._db_with_mock_query("mssql")
        captured = {}

        def fake_query(name, query, params=None):
            captured["query"] = query
            return pd.DataFrame({"TABLE_NAME": []})

        with patch.object(db, "query_dataframe", side_effect=fake_query):
            db.get_tables("conn")

        assert "INFORMATION_SCHEMA" in captured["query"]

    def test_unsupported_dialect_raises_in_get_tables(self):
        """get_tables() should raise ValueError for an unsupported dialect."""
        db = DatabaseManager()
        db.add_connection("bad", connection_string="oracle://x", dialect="oracle")
        with pytest.raises(ValueError, match="Unsupported dialect"):
            db.get_tables("bad")


# ---------------------------------------------------------------------------
# get_columns validation
# ---------------------------------------------------------------------------


class TestGetColumnsValidation:
    """Tests for get_columns() input validation."""

    def test_invalid_table_name_raises(self, db):
        """Table names with unsupported characters should raise ValueError."""
        db.add_connection("conn", connection_string="sqlite:///x.db", dialect="mssql")
        with pytest.raises(ValueError, match="Table name"):
            db.get_columns("conn", "bad-table!")

    def test_invalid_schema_name_raises(self, db):
        """Schema names with unsupported characters should raise ValueError."""
        db.add_connection("conn2", connection_string="sqlite:///x.db", dialect="mssql")
        with pytest.raises(ValueError, match="Schema name"):
            db.get_columns("conn2", "valid_table", schema="bad schema!")

    def test_unsupported_dialect_raises_in_get_columns(self, db):
        """get_columns() should raise ValueError for an unsupported dialect."""
        db.add_connection("bad", connection_string="sqlite:///x.db", dialect="sqlite")
        # SQLite is not handled in get_columns; should raise
        with pytest.raises(ValueError, match="Unsupported dialect"):
            db.get_columns("bad", "sometable")


# ---------------------------------------------------------------------------
# db_manager singleton
# ---------------------------------------------------------------------------


class TestDbManagerSingleton:
    """Tests for the module-level db_manager instance."""

    def test_is_database_manager_instance(self):
        """db_manager should be a DatabaseManager instance."""
        from aiml_dash.utils.database import db_manager

        assert isinstance(db_manager, DatabaseManager)


# ---------------------------------------------------------------------------
# get_connection (mocked pyodbc)
# ---------------------------------------------------------------------------


class TestGetConnection:
    """Tests for DatabaseManager.get_connection with a mocked pyodbc."""

    def test_returns_connection_object(self, db):
        """get_connection() should return the connection object from pyodbc.connect."""
        db.add_connection("c1", connection_string="DRIVER=test;SERVER=srv;DATABASE=db")
        mock_conn = MagicMock()
        mock_pyodbc = MagicMock()
        mock_pyodbc.connect.return_value = mock_conn
        with patch.dict("sys.modules", {"pyodbc": mock_pyodbc}):
            result = db.get_connection("c1")
        assert result is mock_conn

    def test_raises_import_error_without_pyodbc(self, db):
        """get_connection() should raise ImportError when pyodbc is absent."""
        db.add_connection("c2", connection_string="DRIVER=test")
        with patch.dict("sys.modules", {"pyodbc": None}):
            with pytest.raises(ImportError, match="pyodbc"):
                db.get_connection("c2")


# ---------------------------------------------------------------------------
# get_engine (mocked sqlalchemy)
# ---------------------------------------------------------------------------


class TestGetEngine:
    """Tests for DatabaseManager.get_engine with mocked sqlalchemy."""

    def test_returns_engine(self, db):
        """get_engine() should return the engine created by create_engine."""
        db.add_connection("eng1", connection_string="sqlite:///test.db", dialect="sqlite")
        mock_engine = MagicMock()
        mock_sqlalchemy = MagicMock()
        mock_sqlalchemy.create_engine.return_value = mock_engine

        with patch.dict("sys.modules", {"sqlalchemy": mock_sqlalchemy}):
            result = db.get_engine("eng1")

        assert result is mock_engine

    def test_returns_cached_engine_on_second_call(self, db):
        """get_engine() should return the cached engine without re-creating."""
        db.add_connection("eng2", connection_string="sqlite:///test2.db", dialect="sqlite")
        mock_engine = MagicMock()
        mock_sqlalchemy = MagicMock()
        mock_sqlalchemy.create_engine.return_value = mock_engine

        with patch.dict("sys.modules", {"sqlalchemy": mock_sqlalchemy}):
            e1 = db.get_engine("eng2")
            e2 = db.get_engine("eng2")

        assert e1 is e2
        mock_sqlalchemy.create_engine.assert_called_once()

    def test_mssql_uses_odbc_connect(self, db):
        """get_engine() for MSSQL should wrap the connection string for ODBC."""
        db.add_connection(
            "mssql1",
            connection_string="DRIVER={SQL Server};SERVER=srv",
            dialect="mssql",
        )
        mock_engine = MagicMock()
        mock_sqlalchemy = MagicMock()
        mock_sqlalchemy.create_engine.return_value = mock_engine

        with patch.dict("sys.modules", {"sqlalchemy": mock_sqlalchemy}):
            db.get_engine("mssql1")

        call_args = mock_sqlalchemy.create_engine.call_args[0][0]
        assert "mssql+pyodbc" in call_args


# ---------------------------------------------------------------------------
# connection_context
# ---------------------------------------------------------------------------


class TestConnectionContext:
    """Tests for DatabaseManager.connection_context."""

    def test_yields_connection_and_closes(self, db):
        """connection_context() should yield the connection and close it afterwards."""
        db.add_connection("ctx1", connection_string="sqlite:///x.db")
        mock_conn = MagicMock()

        with patch.object(db, "get_connection", return_value=mock_conn):
            with db.connection_context("ctx1") as conn:
                assert conn is mock_conn

        mock_conn.close.assert_called_once()

    def test_closes_connection_on_exception(self, db):
        """connection_context() should close the connection even if an exception occurs."""
        db.add_connection("ctx2", connection_string="sqlite:///x.db")
        mock_conn = MagicMock()

        with patch.object(db, "get_connection", return_value=mock_conn):
            with pytest.raises(RuntimeError):
                with db.connection_context("ctx2"):
                    raise RuntimeError("test")

        mock_conn.close.assert_called_once()


# ---------------------------------------------------------------------------
# query_dataframe
# ---------------------------------------------------------------------------


class TestQueryDataframe:
    """Tests for DatabaseManager.query_dataframe."""

    def test_uses_engine_by_default(self, db):
        """query_dataframe() should use a SQLAlchemy engine when use_engine=True."""
        db.add_connection("qd1", connection_string="sqlite:///x.db", dialect="sqlite", use_sqlalchemy=True)
        mock_engine = MagicMock()
        expected_df = pd.DataFrame({"col": [1, 2]})

        with patch.object(db, "get_engine", return_value=mock_engine), \
             patch("aiml_dash.utils.database.pd.read_sql", return_value=expected_df) as mock_rs:
            result = db.query_dataframe("qd1", "SELECT 1")

        assert result is expected_df

    def test_uses_raw_connection_when_engine_disabled(self, db):
        """query_dataframe() should use a raw connection when use_engine=False."""
        db.add_connection("qd2", connection_string="sqlite:///x.db", dialect="sqlite")
        mock_conn = MagicMock()
        expected_df = pd.DataFrame({"col": [3, 4]})

        with patch.object(db, "get_connection", return_value=mock_conn), \
             patch("aiml_dash.utils.database.pd.read_sql", return_value=expected_df):
            result = db.query_dataframe("qd2", "SELECT 1", use_engine=False)

        assert result is expected_df

    def test_raises_on_write_query(self, db):
        """query_dataframe() should raise ValueError for non-read-only queries."""
        db.add_connection("qd3", connection_string="sqlite:///x.db")
        with pytest.raises(ValueError, match="read-only"):
            db.query_dataframe("qd3", "DELETE FROM t")


# ---------------------------------------------------------------------------
# execute_query
# ---------------------------------------------------------------------------


class TestExecuteQuery:
    """Tests for DatabaseManager.execute_query."""

    def test_returns_row_count(self, db):
        """execute_query() should return the cursor's rowcount."""
        db.add_connection("eq1", connection_string="sqlite:///x.db")
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 5
        mock_conn.cursor.return_value = mock_cursor

        with patch.object(db, "get_connection", return_value=mock_conn):
            count = db.execute_query("eq1", "INSERT INTO t VALUES (1)")

        assert count == 5

    def test_commits_by_default(self, db):
        """execute_query() should commit the connection by default."""
        db.add_connection("eq2", connection_string="sqlite:///x.db")
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1
        mock_conn.cursor.return_value = mock_cursor

        with patch.object(db, "get_connection", return_value=mock_conn):
            db.execute_query("eq2", "UPDATE t SET x=1")

        mock_conn.commit.assert_called_once()

    def test_no_commit_when_commit_false(self, db):
        """execute_query() should not commit when commit=False."""
        db.add_connection("eq3", connection_string="sqlite:///x.db")
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1
        mock_conn.cursor.return_value = mock_cursor

        with patch.object(db, "get_connection", return_value=mock_conn):
            db.execute_query("eq3", "UPDATE t SET x=1", commit=False)

        mock_conn.commit.assert_not_called()


# ---------------------------------------------------------------------------
# get_tables with schema filter
# ---------------------------------------------------------------------------


class TestGetTablesWithSchema:
    """Tests for get_tables() schema filter logic."""

    def test_mssql_schema_filter_appended(self):
        """get_tables() for MSSQL with schema should include AND TABLE_SCHEMA clause."""
        db = DatabaseManager()
        db.add_connection("conn", connection_string="x", dialect="mssql")
        captured = {}

        def fake_query(name, query, params=None):
            captured["query"] = query
            captured["params"] = params
            return pd.DataFrame({"TABLE_NAME": []})

        with patch.object(db, "query_dataframe", side_effect=fake_query):
            db.get_tables("conn", schema="dbo")

        assert "TABLE_SCHEMA" in captured["query"]
        assert captured["params"] == {"schema": "dbo"}

    def test_postgresql_routing(self):
        """get_tables() for postgresql should use information_schema.tables."""
        db = DatabaseManager()
        db.add_connection("pgconn", connection_string="x", dialect="postgresql")
        captured = {}

        def fake_query(name, query, params=None):
            captured["query"] = query
            return pd.DataFrame({"table_name": []})

        with patch.object(db, "query_dataframe", side_effect=fake_query):
            db.get_tables("pgconn")

        assert "information_schema" in captured["query"].lower()

    def test_mysql_routing(self):
        """get_tables() for MySQL should use information_schema.tables."""
        db = DatabaseManager()
        db.add_connection("myconn", connection_string="x", dialect="mysql")
        captured = {}

        def fake_query(name, query, params=None):
            captured["query"] = query
            return pd.DataFrame({"table_name": []})

        with patch.object(db, "query_dataframe", side_effect=fake_query):
            db.get_tables("myconn")

        assert "information_schema" in captured["query"].lower()


# ---------------------------------------------------------------------------
# get_columns routing
# ---------------------------------------------------------------------------


class TestGetColumnsRouting:
    """Tests for get_columns() dialect routing."""

    def test_mssql_get_columns_query(self):
        """get_columns() for MSSQL should query INFORMATION_SCHEMA.COLUMNS."""
        db = DatabaseManager()
        db.add_connection("conn", connection_string="x", dialect="mssql")
        captured = {}

        def fake_query(name, query, params=None):
            captured["query"] = query
            captured["params"] = params
            return pd.DataFrame()

        with patch.object(db, "query_dataframe", side_effect=fake_query):
            db.get_columns("conn", "my_table")

        assert "INFORMATION_SCHEMA.COLUMNS" in captured["query"]
        assert captured["params"]["table"] == "my_table"

    def test_mssql_get_columns_with_schema(self):
        """get_columns() for MSSQL with schema should add TABLE_SCHEMA clause."""
        db = DatabaseManager()
        db.add_connection("conn2", connection_string="x", dialect="mssql")
        captured = {}

        def fake_query(name, query, params=None):
            captured["query"] = query
            captured["params"] = params
            return pd.DataFrame()

        with patch.object(db, "query_dataframe", side_effect=fake_query):
            db.get_columns("conn2", "my_table", schema="dbo")

        assert "TABLE_SCHEMA" in captured["query"]
        assert captured["params"]["schema"] == "dbo"

    def test_postgresql_get_columns_query(self):
        """get_columns() for PostgreSQL should query information_schema.columns."""
        db = DatabaseManager()
        db.add_connection("pgconn", connection_string="x", dialect="postgresql")
        captured = {}

        def fake_query(name, query, params=None):
            captured["query"] = query
            return pd.DataFrame()

        with patch.object(db, "query_dataframe", side_effect=fake_query):
            db.get_columns("pgconn", "my_table")

        assert "information_schema.columns" in captured["query"].lower()

    def test_mysql_get_columns_query(self):
        """get_columns() for MySQL should query information_schema.columns."""
        db = DatabaseManager()
        db.add_connection("myconn", connection_string="x", dialect="mysql")
        captured = {}

        def fake_query(name, query, params=None):
            captured["query"] = query
            return pd.DataFrame()

        with patch.object(db, "query_dataframe", side_effect=fake_query):
            db.get_columns("myconn", "my_table")

        assert "information_schema.columns" in captured["query"].lower()
