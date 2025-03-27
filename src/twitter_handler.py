"""Twitter API integration handler for the Twitter Manager."""
import time
from typing import Optional
from datetime import datetime, timedelta

import tweepy
from tweepy.errors import TweepyException

from .config import (
    TWITTER_API_KEY,
    TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET,
    BEARER_TOKEN,
    MAX_TWEETS_PER_DAY,
    RATE_LIMIT_BUFFER
)

class TwitterHandler:
    """Handles all Twitter API interactions."""
    
    def __init__(self):
        """Initialize the Twitter API client."""
        self.client = self._initialize_client()
        self._last_tweet_time = None
        self._daily_tweet_count = 0
        self._reset_daily_count()

    def _initialize_client(self) -> tweepy.Client:
        """
        Initialize and return the Twitter API client.
        
        Returns:
            tweepy.Client: Authenticated Twitter client
        """
        return tweepy.Client(
            bearer_token=BEARER_TOKEN,
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_TOKEN_SECRET,
            wait_on_rate_limit=True
        )

    def post_tweet(self, content: str) -> Optional[str]:
        """
        Post a tweet to Twitter.
        
        Args:
            content: The content to tweet
            
        Returns:
            Optional[str]: Tweet ID if successful, None if failed
            
        Raises:
            RateLimitError: If tweet limit has been reached
            TweepyException: For other Twitter API errors
        """
        if not self._can_tweet():
            raise RateLimitError("Tweet limit reached for today")

        try:
            # Post the tweet using v2 endpoint
            response = self.client.create_tweet(text=content)
            
            # Update tracking
            self._last_tweet_time = datetime.now()
            self._daily_tweet_count += 1
            
            # Handle the v2 response format
            if hasattr(response, 'data') and 'id' in response.data:
                return response.data['id']
            return None
            
        except TweepyException as e:
            # Print detailed error information for debugging
            print(f"Twitter API Error: {str(e)}")
            if hasattr(e, 'response'):
                print(f"Response Status: {e.response.status_code}")
                print(f"Response Text: {e.response.text}")
            
            # Handle rate limits and other Twitter API errors
            if hasattr(e, 'response') and e.response.status_code == 429:  # Rate limit exceeded
                print(e)
                self._handle_rate_limit(e)
            raise

    def _can_tweet(self) -> bool:
        """
        Check if we can post another tweet based on rate limits.
        
        Returns:
            bool: True if we can tweet, False otherwise
        """
        # Reset daily count if needed
        self._reset_daily_count()
        
        # Check if we're under our daily limit with buffer
        max_tweets = int(MAX_TWEETS_PER_DAY * RATE_LIMIT_BUFFER)
        return self._daily_tweet_count < max_tweets

    def _reset_daily_count(self) -> None:
        """Reset the daily tweet count if it's a new day."""
        now = datetime.now()
        
        # If this is the first tweet or it's a new day
        if (self._last_tweet_time is None or 
            now.date() > self._last_tweet_time.date()):
            self._daily_tweet_count = 0
            self._last_tweet_time = now

    def _handle_rate_limit(self, error: TweepyException) -> None:
        """
        Handle rate limit errors by updating internal tracking.
        
        Args:
            error: The Tweepy error that occurred
        """
        # Update our count to match Twitter's tracking
        self._daily_tweet_count = MAX_TWEETS_PER_DAY
        
        # Log the rate limit reset time
        if hasattr(error, 'response') and 'x-rate-limit-reset' in error.response.headers:
            reset_time = int(error.response.headers['x-rate-limit-reset'])
            self._last_tweet_time = datetime.fromtimestamp(reset_time)

    def delete_tweet(self, tweet_id: str) -> bool:
        """
        Delete a tweet by ID.
        
        Args:
            tweet_id: The ID of the tweet to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            self.client.delete_tweet(tweet_id)
            return True
        except TweepyException:
            return False

    def verify_credentials(self) -> bool:
        """
        Verify that the API credentials are valid.
        
        Returns:
            bool: True if credentials are valid, False otherwise
        """
        try:
            user = self.client.get_me()
            print(f"Authenticated as user: {user.data}")
            return True
        except TweepyException as e:
            print(f"Authentication Error: {str(e)}")
            return False

class RateLimitError(Exception):
    """Raised when tweet rate limit is reached."""
    pass