"""Tests for the Twitter handler module."""
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from src.twitter_handler import TwitterHandler, RateLimitError

class TestTwitterHandler(unittest.TestCase):
    """Test cases for TwitterHandler class."""

    def setUp(self):
        """Set up test fixtures."""
        self.handler = TwitterHandler()

    @patch('tweepy.Client')
    def test_post_tweet_success(self, mock_client):
        """Test successful tweet posting."""
        # Mock the tweepy client
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        
        # Mock successful tweet response
        mock_response = MagicMock()
        mock_response.data = {'id': '123456789'}
        mock_client_instance.create_tweet.return_value = mock_response
        
        # Create handler with mocked client
        handler = TwitterHandler()
        
        # Test posting
        tweet_id = handler.post_tweet("Test tweet content")
        
        # Verify the result
        self.assertEqual(tweet_id, '123456789')
        mock_client_instance.create_tweet.assert_called_once_with(
            text="Test tweet content"
        )

    @patch('tweepy.Client')
    def test_rate_limit_handling(self, mock_client):
        """Test rate limit handling."""
        # Mock the tweepy client
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        
        # Create handler with mocked client
        handler = TwitterHandler()
        
        # Simulate reaching rate limit
        handler._daily_tweet_count = 24  # Max tweets per day
        
        # Test posting should raise RateLimitError
        with self.assertRaises(RateLimitError):
            handler.post_tweet("Test tweet")

    @patch('tweepy.Client')
    def test_daily_count_reset(self, mock_client):
        """Test daily tweet count reset."""
        # Mock the tweepy client
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        
        # Create handler with mocked client
        handler = TwitterHandler()
        
        # Set last tweet time to yesterday
        handler._last_tweet_time = datetime.now() - timedelta(days=1)
        handler._daily_tweet_count = 24
        
        # Verify count is reset when posting
        self.assertTrue(handler._can_tweet())
        self.assertEqual(handler._daily_tweet_count, 0)

    @patch('tweepy.Client')
    def test_verify_credentials_success(self, mock_client):
        """Test successful credentials verification."""
        # Mock the tweepy client
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        
        # Mock successful verification
        mock_client_instance.get_me.return_value = MagicMock()
        
        # Create handler with mocked client
        handler = TwitterHandler()
        
        # Test verification
        self.assertTrue(handler.verify_credentials())
        mock_client_instance.get_me.assert_called_once()

    @patch('tweepy.Client')
    def test_verify_credentials_failure(self, mock_client):
        """Test failed credentials verification."""
        # Mock the tweepy client
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        
        # Mock failed verification
        mock_client_instance.get_me.side_effect = Exception("Invalid credentials")
        
        # Create handler with mocked client
        handler = TwitterHandler()
        
        # Test verification
        self.assertFalse(handler.verify_credentials())

    @patch('tweepy.Client')
    def test_delete_tweet_success(self, mock_client):
        """Test successful tweet deletion."""
        # Mock the tweepy client
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        
        # Create handler with mocked client
        handler = TwitterHandler()
        
        # Test deletion
        self.assertTrue(handler.delete_tweet('123456789'))
        mock_client_instance.delete_tweet.assert_called_once_with('123456789')

    @patch('tweepy.Client')
    def test_delete_tweet_failure(self, mock_client):
        """Test failed tweet deletion."""
        # Mock the tweepy client
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        
        # Mock deletion failure
        mock_client_instance.delete_tweet.side_effect = Exception("Tweet not found")
        
        # Create handler with mocked client
        handler = TwitterHandler()
        
        # Test deletion
        self.assertFalse(handler.delete_tweet('123456789'))

if __name__ == '__main__':
    unittest.main()