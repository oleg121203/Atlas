"""
Tests for the DatabaseOptimizer class in utils/db_optimizer.py
"""

import pytest

from utils.db_optimizer import DatabaseOptimizer


@pytest.fixture
def db_path(tmp_path):
    """Create a temporary database file path."""
    return str(tmp_path / "test_db.sqlite3")


@pytest.fixture
def optimizer(db_path):
    """Create an instance of DatabaseOptimizer for testing."""
    optimizer = DatabaseOptimizer(db_path)
    optimizer.connect()

    # Check if connection was successful
    if optimizer.conn and optimizer.cursor:
        # Create a test table
        optimizer.cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_table (
                id INTEGER PRIMARY KEY,
                name TEXT,
                category TEXT,
                value INTEGER
            )
        """)
        optimizer.conn.commit()

    yield optimizer

    # Clean up
    optimizer.close()


def test_connect_and_close(db_path):
    """Test connecting to and closing a database."""
    optimizer = DatabaseOptimizer(db_path)

    # Test connect
    optimizer.connect()
    assert optimizer.conn is not None
    assert optimizer.cursor is not None

    # Test close
    optimizer.close()
    assert optimizer.conn is None
    assert optimizer.cursor is None


def test_create_indexes(optimizer):
    """Test creating indexes on tables."""
    # Define indexes to create
    indexes = [
        {"name": "idx_test_name", "table": "test_table", "columns": ["name"]},
        {"name": "idx_test_category", "table": "test_table", "columns": ["category"]},
        {
            "name": "idx_test_combined",
            "table": "test_table",
            "columns": ["category", "value"],
        },
    ]

    # Create indexes
    optimizer.create_indexes(indexes)

    # Check if indexes were created
    optimizer.cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
    created_indexes = [row[0] for row in optimizer.cursor.fetchall()]

    assert "idx_test_name" in created_indexes
    assert "idx_test_category" in created_indexes
    assert "idx_test_combined" in created_indexes


def test_create_index_if_not_exists(optimizer):
    """Test creating an index only if it doesn't exist."""
    # Create an index
    optimizer.create_indexes(
        [{"name": "idx_test_value", "table": "test_table", "columns": ["value"]}]
    )

    # Try to create the same index again
    optimizer.create_indexes(
        [{"name": "idx_test_value", "table": "test_table", "columns": ["value"]}]
    )

    # Should succeed without errors
    optimizer.cursor.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND name='idx_test_value'"
    )
    count = optimizer.cursor.fetchone()[0]
    assert count == 1


def test_execute_query(optimizer):
    """Test executing a basic query."""
    # Insert some test data
    if optimizer.conn and optimizer.cursor:
        for i in range(100):
            optimizer.cursor.execute(
                "INSERT INTO test_table (name, category, value) VALUES (?, ?, ?)",
                (f"Item {i}", f"Category {i % 5}", i),
            )
        optimizer.conn.commit()

        # Execute a simple query
        optimizer.cursor.execute(
            "SELECT * FROM test_table WHERE category = 'Category 1'"
        )
        results = optimizer.cursor.fetchall()

        # Verify results
        assert len(results) > 0
        assert all(row[2] == "Category 1" for row in results)


def test_transaction_management(optimizer):
    """Test transaction management with commit and rollback."""
    if optimizer.conn and optimizer.cursor:
        # Start a transaction
        optimizer.cursor.execute(
            "INSERT INTO test_table (name, category, value) VALUES (?, ?, ?)",
            ("Transaction Test", "Test Category", 999),
        )

        # Verify item exists before rollback
        optimizer.cursor.execute(
            "SELECT * FROM test_table WHERE name = 'Transaction Test'"
        )
        before_rollback = optimizer.cursor.fetchall()
        assert len(before_rollback) == 1

        # Rollback the transaction
        optimizer.conn.rollback()

        # Verify item doesn't exist after rollback
        optimizer.cursor.execute(
            "SELECT * FROM test_table WHERE name = 'Transaction Test'"
        )
        after_rollback = optimizer.cursor.fetchall()
        assert len(after_rollback) == 0


def test_index_performance(optimizer):
    """Test that indexes improve query performance."""
    if optimizer.conn and optimizer.cursor:
        # Insert a larger dataset
        for i in range(1000):
            optimizer.cursor.execute(
                "INSERT INTO test_table (name, category, value) VALUES (?, ?, ?)",
                (f"Performance Item {i}", f"Performance Category {i % 10}", i),
            )
        optimizer.conn.commit()

        # Create an index for the test
        optimizer.create_indexes(
            [{"name": "idx_perf_test", "table": "test_table", "columns": ["value"]}]
        )

        # Execute a query that should use the index
        optimizer.cursor.execute("SELECT * FROM test_table WHERE value > 950")
        results = optimizer.cursor.fetchall()

        # Verify results
        assert len(results) == 49  # Items 951-999 inclusive


def test_failed_connection():
    """Test handling a failed database connection."""
    # Use an invalid path that should fail to connect
    optimizer = DatabaseOptimizer("/invalid/path/that/doesnt/exist/db.sqlite")

    # This should not raise an exception
    optimizer.connect()

    # Connection should be None
    assert optimizer.conn is None
    assert optimizer.cursor is None


def test_multiple_index_creation(optimizer):
    """Test creating multiple indexes in one go."""
    if optimizer.conn and optimizer.cursor:
        # Define multiple indexes
        multi_indexes = [
            {"name": "idx_multi_name", "table": "test_table", "columns": ["name"]},
            {"name": "idx_multi_cat", "table": "test_table", "columns": ["category"]},
            {"name": "idx_multi_val", "table": "test_table", "columns": ["value"]},
        ]

        # Create all indexes
        optimizer.create_indexes(multi_indexes)

        # Check if all indexes were created
        optimizer.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_multi_%'"
        )
        created_indexes = [row[0] for row in optimizer.cursor.fetchall()]

        assert len(created_indexes) == 3
        assert "idx_multi_name" in created_indexes
        assert "idx_multi_cat" in created_indexes
        assert "idx_multi_val" in created_indexes
