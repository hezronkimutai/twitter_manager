"""Tests for the database manager module."""
import unittest
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import os

from src.db_manager import DatabaseManager

class TestDatabaseManager(unittest.TestCase):
    """Test cases for DatabaseManager class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test database
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test.db"
        
        # Patch the DB_PATH in the manager
        self._original_db_path = DatabaseManager.db_path
        DatabaseManager.db_path = self.db_path
        
        # Create manager instance
        self.manager = DatabaseManager()

    def tearDown(self):
        """Clean up test fixtures."""
        # Restore original DB_PATH
        DatabaseManager.db_path = self._original_db_path
        
        # Remove test database
        if self.db_path.exists():
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)

    def test_create_tables(self):
        """Test database table creation."""
        # Verify table exists and has correct schema
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='posts'
            """)
            self.assertIsNotNone(cursor.fetchone())
            
            # Check columns
            cursor.execute("PRAGMA table_info(posts)")
            columns = {row[1] for row in cursor.fetchall()}
            expected_columns = {
                'id', 'content', 'posted_at', 'status', 'error_message'
            }
            self.assertEqual(columns, expected_columns)

    def test_add_post(self):
        """Test adding a new post."""
        content = "Test tweet content"
        post_id = self.manager.add_post(content)
        
        # Verify post was added
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
            row = cursor.fetchone()
            
            self.assertIsNotNone(row)
            self.assertEqual(row[1], content)  # Check content
            self.assertEqual(row[3], "pending")  # Check status

    def test_update_post_status(self):
        """Test updating post status."""
        # Add a test post
        post_id = self.manager.add_post("Test content")
        
        # Update status to success
        self.manager.update_post_status(post_id, "success")
        
        # Verify status was updated
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status, posted_at FROM posts WHERE id = ?", 
                         (post_id,))
            row = cursor.fetchone()
            
            self.assertEqual(row[0], "success")
            self.assertIsNotNone(row[1])  # posted_at should be set

    def test_get_post_history(self):
        """Test retrieving post history."""
        # Add some test posts
        contents = ["Test 1", "Test 2", "Test 3"]
        for content in contents:
            self.manager.add_post(content)
            
        # Get history
        history = self.manager.get_post_history(limit=2)
        
        # Verify results
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["content"], "Test 3")
        self.assertEqual(history[1]["content"], "Test 2")

    def test_get_post_stats(self):
        """Test retrieving post statistics."""
        # Add posts with different statuses
        self.manager.add_post("Success 1")
        self.manager.update_post_status(1, "success")
        
        self.manager.add_post("Failed 1")
        self.manager.update_post_status(2, "failed", "Error message")
        
        self.manager.add_post("Pending 1")
        
        # Get stats
        stats = self.manager.get_post_stats()
        
        # Verify stats
        self.assertEqual(stats["total_posts"], 3)
        self.assertEqual(stats["successful_posts"], 1)
        self.assertEqual(stats["failed_posts"], 1)
        self.assertEqual(stats["pending_posts"], 1)

    def test_is_content_duplicate(self):
        """Test duplicate content checking."""
        content = "Unique test content"
        duplicate = "Duplicate test content"
        
        # Add initial posts
        self.manager.add_post(duplicate)
        
        # Test duplicate check
        self.assertTrue(self.manager.is_content_duplicate(duplicate))
        self.assertFalse(self.manager.is_content_duplicate(content))

    def test_cleanup_old_failed_posts(self):
        """Test cleaning up old failed posts."""
        # Add some failed posts with old timestamps
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            old_date = datetime.now() - timedelta(days=31)
            cursor.execute("""
                INSERT INTO posts (content, status, posted_at)
                VALUES (?, ?, ?)
            """, ("Old failed post", "failed", old_date.isoformat()))
            
            recent_date = datetime.now() - timedelta(days=1)
            cursor.execute("""
                INSERT INTO posts (content, status, posted_at)
                VALUES (?, ?, ?)
            """, ("Recent failed post", "failed", recent_date.isoformat()))
            
        # Run cleanup
        self.manager.cleanup_old_failed_posts(days=30)
        
        # Verify old post was removed but recent one remains
        cursor.execute("SELECT COUNT(*) FROM posts")
        self.assertEqual(cursor.fetchone()[0], 1)

if __name__ == '__main__':
    unittest.main()