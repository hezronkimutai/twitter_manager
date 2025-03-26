"""Database management for the Twitter Manager."""
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict
from pathlib import Path

from .config import DB_PATH

class DatabaseManager:
    """Manages all database operations for the Twitter Manager."""
    
    def __init__(self):
        """Initialize the database connection and create tables if they don't exist."""
        self.db_path = DB_PATH
        self._create_tables()

    def _create_tables(self) -> None:
        """Create the necessary database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    posted_at TIMESTAMP,
                    status TEXT NOT NULL,
                    error_message TEXT
                )
            """)
            conn.commit()

    def add_post(self, content: str) -> int:
        """
        Add a new post to the database with 'pending' status.
        
        Args:
            content: The content of the post
            
        Returns:
            int: The ID of the newly created post
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO posts (content, status) VALUES (?, ?)",
                (content, "pending")
            )
            conn.commit()
            return cursor.lastrowid

    def update_post_status(self, post_id: int, status: str, error_message: Optional[str] = None) -> None:
        """
        Update the status of a post.
        
        Args:
            post_id: The ID of the post to update
            status: The new status ('success', 'failed', or 'pending')
            error_message: Optional error message if the post failed
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if status == "success":
                cursor.execute(
                    "UPDATE posts SET status = ?, posted_at = ? WHERE id = ?",
                    (status, datetime.now(), post_id)
                )
            else:
                cursor.execute(
                    "UPDATE posts SET status = ?, error_message = ? WHERE id = ?",
                    (status, error_message, post_id)
                )
            conn.commit()

    def get_post_history(self, limit: int = 10) -> List[Dict]:
        """
        Get the history of posts with their statuses.
        
        Args:
            limit: Maximum number of posts to retrieve
            
        Returns:
            List of dictionaries containing post information
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM posts 
                ORDER BY posted_at DESC 
                LIMIT ?
                """,
                (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_post_stats(self) -> Dict:
        """
        Get statistics about posts.
        
        Returns:
            Dictionary containing post statistics
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending
                FROM posts
            """)
            row = cursor.fetchone()
            return {
                "total_posts": row[0],
                "successful_posts": row[1],
                "failed_posts": row[2],
                "pending_posts": row[3]
            }

    def is_content_duplicate(self, content: str) -> bool:
        """
        Check if content has been posted before.
        
        Args:
            content: The content to check
            
        Returns:
            bool: True if content is a duplicate, False otherwise
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM posts WHERE content = ?",
                (content,)
            )
            return cursor.fetchone()[0] > 0

    def cleanup_old_failed_posts(self, days: int = 30) -> None:
        """
        Remove failed posts older than specified days.
        
        Args:
            days: Number of days after which to remove failed posts
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                DELETE FROM posts 
                WHERE status = 'failed' 
                AND posted_at < date('now', ?)
                """,
                (f'-{days} days',)
            )
            conn.commit()