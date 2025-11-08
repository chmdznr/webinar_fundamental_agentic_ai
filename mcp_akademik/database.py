"""
Database connection module for MCP Server Akademik.

Provides safe database connection and query execution for the kampus.db SQLite database.
"""

import sqlite3
from pathlib import Path
from typing import Optional, List, Tuple, Any


class DatabaseConnection:
    """
    Manages SQLite database connections for the academic server.

    This class provides a context manager for safe database operations
    and helper methods for common query patterns.
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database connection manager.

        Args:
            db_path (str, optional): Path to SQLite database file.
                                     Defaults to ../database/kampus.db
        """
        if db_path is None:
            # Default path: go up one directory, then into database/
            script_dir = Path(__file__).parent
            self.db_path = script_dir.parent / "database" / "kampus.db"
        else:
            self.db_path = Path(db_path)

        # Verify database exists
        if not self.db_path.exists():
            raise FileNotFoundError(
                f"Database file not found: {self.db_path}\n"
                f"Please run database/setup_database.py first"
            )

    def execute_query(
        self,
        query: str,
        params: Tuple[Any, ...] = (),
        fetch_one: bool = False
    ) -> Optional[List[Tuple[Any, ...]]]:
        """
        Execute a SQL query safely with parameters.

        Args:
            query (str): SQL query with ? placeholders
            params (tuple): Parameters to bind to query placeholders
            fetch_one (bool): If True, return only first result

        Returns:
            List of tuples (query results) or None if no results
            If fetch_one=True, returns single tuple or None

        Example:
            >>> db = DatabaseConnection()
            >>> results = db.execute_query(
            ...     "SELECT nama_dosen FROM dosen WHERE id = ?",
            ...     (1,)
            ... )
            >>> print(results)
            [('Dr. Budi Santoso',)]
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Execute query with parameterized binding (prevents SQL injection)
            cursor.execute(query, params)

            if fetch_one:
                result = cursor.fetchone()
            else:
                result = cursor.fetchall()

            conn.close()

            return result

        except sqlite3.Error as e:
            # Log error and return None instead of crashing
            print(f"Database error: {e}")
            print(f"Query: {query}")
            print(f"Params: {params}")
            return None

    def test_connection(self) -> bool:
        """
        Test database connectivity and verify tables exist.

        Returns:
            bool: True if connection successful and tables exist

        Example:
            >>> db = DatabaseConnection()
            >>> if db.test_connection():
            ...     print("Database ready!")
        """
        try:
            result = self.execute_query(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )

            if result:
                tables = [row[0] for row in result]
                required_tables = {'dosen', 'mahasiswa', 'mata_kuliah', 'transkrip'}
                return required_tables.issubset(set(tables))

            return False

        except Exception as e:
            print(f"Connection test failed: {e}")
            return False


# Module-level singleton for convenience
_db_instance: Optional[DatabaseConnection] = None


def get_db() -> DatabaseConnection:
    """
    Get or create the singleton database connection instance.

    Returns:
        DatabaseConnection: Shared database connection instance

    Example:
        >>> from database import get_db
        >>> db = get_db()
        >>> results = db.execute_query("SELECT * FROM dosen")
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseConnection()
    return _db_instance
