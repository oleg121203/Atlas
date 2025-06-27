"""
Database Optimizer Module for Atlas.
This module provides utilities to optimize database queries for improved performance.
"""

import sqlite3
import time
from typing import Any, Dict, List


class DatabaseOptimizer:
    """
    A class to manage database query optimization for Atlas.
    """

    def __init__(self, db_path: str):
        """
        Initialize the DatabaseOptimizer with a path to the SQLite database.

        Args:
            db_path (str): Path to the SQLite database file.
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def connect(self) -> None:
        """
        Establish connection to the SQLite database.
        """
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            print("Connected to SQLite database successfully.")
        except sqlite3.Error as e:
            print(f"Failed to connect to SQLite database: {e}")

    def close(self) -> None:
        """
        Close connection to the SQLite database.
        """
        if self.conn:
            self.conn.close()
            print("SQLite database connection closed.")
            self.conn = None
            self.cursor = None

    def create_indexes(self, indexes: List[Dict[str, Any]]) -> None:
        """
        Create indexes on frequently queried columns to speed up SELECT operations.

        Args:
            indexes (List[Dict[str, Any]]): List of dictionaries defining indexes to create.
                Each dictionary should have 'name', 'table', and 'columns' keys.
        """
        if not self.conn:
            self.connect()
        if not self.conn:
            return

        for index in indexes:
            try:
                index_name = index["name"]
                table_name = index["table"]
                columns = ", ".join(index["columns"])
                query = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({columns})"
                self.cursor.execute(query)
                self.conn.commit()
                print(f"Created index {index_name} on {table_name}({columns})")
            except sqlite3.Error as e:
                print(f"Error creating index {index_name}: {e}")

    def analyze_query(self, query: str, params: tuple = ()) -> Dict[str, Any]:
        """
        Analyze the performance of a given query using EXPLAIN QUERY PLAN.

        Args:
            query (str): SQL query to analyze.
            params (tuple): Parameters for the query if parameterized.

        Returns:
            Dict[str, Any]: Dictionary with analysis results including execution time and plan.
        """
        if not self.conn:
            self.connect()
        if not self.conn:
            return {"error": "Database connection failed"}

        try:
            start_time = time.time()
            explain_query = f"EXPLAIN QUERY PLAN {query}"
            self.cursor.execute(explain_query, params)
            plan = self.cursor.fetchall()
            end_time = time.time()

            return {
                "query": query,
                "execution_time": end_time - start_time,
                "plan": plan,
            }
        except sqlite3.Error as e:
            return {"query": query, "error": str(e)}

    def batch_insert(self, table: str, columns: List[str], data: List[tuple]) -> bool:
        """
        Perform batch insert to reduce the number of transactions.

        Args:
            table (str): Target table for insertion.
            columns (List[str]): List of column names.
            data (List[tuple]): List of tuples containing data to insert.

        Returns:
            bool: True if insert was successful, False otherwise.
        """
        if not self.conn:
            self.connect()
        if not self.conn:
            return False

        try:
            placeholders = ", ".join(["?" for _ in columns])
            col_names = ", ".join(columns)
            query = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})"
            self.cursor.executemany(query, data)
            self.conn.commit()
            print(f"Batch inserted {len(data)} rows into {table}")
            return True
        except sqlite3.Error as e:
            print(f"Error during batch insert into {table}: {e}")
            return False

    def optimize_table(self, table: str) -> None:
        """
        Run PRAGMA optimize and VACUUM on a specific table to improve performance.

        Args:
            table (str): Table to optimize.
        """
        if not self.conn:
            self.connect()
        if not self.conn:
            return

        try:
            self.cursor.execute("PRAGMA optimize")
            self.conn.commit()
            print("Database optimization settings adjusted")

            self.cursor.execute(f"VACUUM {table}")
            self.conn.commit()
            print(f"Vacuumed table {table} to reclaim space")
        except sqlite3.Error as e:
            print(f"Error optimizing table {table}: {e}")


# Example usage
if __name__ == "__main__":
    # Replace with actual path to Atlas database
    db_optimizer = DatabaseOptimizer(":memory:")  # Using in-memory for demo
    db_optimizer.connect()

    # Create a sample table for demonstration
    db_optimizer.cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            title TEXT,
            completed BOOLEAN
        )
    """)
    db_optimizer.conn.commit()

    # Define indexes for frequently queried fields
    indexes_to_create = [
        {"name": "idx_tasks_user_id", "table": "tasks", "columns": ["user_id"]},
        {"name": "idx_tasks_completed", "table": "tasks", "columns": ["completed"]},
    ]
    db_optimizer.create_indexes(indexes_to_create)

    # Analyze a sample query
    analysis = db_optimizer.analyze_query(
        "SELECT * FROM tasks WHERE user_id = ?", ("123",)
    )
    print("Query Analysis:", analysis)

    # Perform a batch insert
    sample_data = [("123", "Task 1", 0), ("123", "Task 2", 1), ("456", "Task 3", 0)]
    db_optimizer.batch_insert("tasks", ["user_id", "title", "completed"], sample_data)

    # Optimize the table
    db_optimizer.optimize_table("tasks")

    db_optimizer.close()
