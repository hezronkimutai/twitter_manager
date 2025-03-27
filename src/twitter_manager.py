"""Main script for the Twitter Manager that orchestrates the entire posting process."""
import logging
import time
from datetime import datetime
import sys
from pathlib import Path
from typing import Optional

from .config import (
    MAX_RETRIES,
    RETRY_DELAY_SECONDS,
    LOG_FORMAT,
    LOG_LEVEL,
    validate_config
)
from .content_generator import ContentGenerator
from .twitter_handler import TwitterHandler, RateLimitError
from .db_manager import DatabaseManager

# Set up logging directory
script_dir = Path(__file__).parent.parent
logs_dir = script_dir / "logs"
logs_dir.mkdir(parents=True, exist_ok=True)

# Set up log file path with timestamp
log_file = logs_dir / f"twitter_manager_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)
logger.info(f"Logging to: {log_file}")

class TwitterManager:
    """Manages the automated Twitter posting process."""
    
    def __init__(self):
        """Initialize the Twitter Manager components."""
        try:
            # Validate configuration
            validate_config()
            
            # Initialize components
            self.content_generator = ContentGenerator()
            self.twitter_handler = TwitterHandler()
            self.db_manager = DatabaseManager()
            
            # Verify Twitter credentials
            if not self.twitter_handler.verify_credentials():
                raise ValueError("Invalid Twitter credentials")
                
            logger.info("Twitter Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Twitter Manager: {str(e)}")
            raise

    def generate_and_post(self) -> bool:
        """
        Generate and post a new tweet.
        
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info("Starting generate and post process")
        
        for attempt in range(MAX_RETRIES):
            try:
                # Generate content
                content = self.content_generator.generate_tweet()
                
                # Validate content
                if not self.content_generator.is_content_appropriate(content):
                    logger.warning("Generated content was not appropriate, retrying...")
                    continue
                    
                # Check for duplicates
                if self.db_manager.is_content_duplicate(content):
                    logger.warning("Generated content was duplicate, retrying...")
                    continue
                
                # Add to database as pending
                post_id = self.db_manager.add_post(content)
                
                # Post to Twitter
                tweet_id = self.twitter_handler.post_tweet(content)
                
                if tweet_id:
                    # Update database with success
                    self.db_manager.update_post_status(post_id, "success")
                    logger.info(f"Successfully posted tweet: {tweet_id}")
                    return True
                    
            except RateLimitError as e:
                logger.error(f"Rate limit reached: {str(e)}")
                self.db_manager.update_post_status(post_id, "failed", str(e))
                return False
                
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                if post_id:
                    self.db_manager.update_post_status(
                        post_id, "failed", str(e)
                    )
                
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY_SECONDS)
                    continue
                
                return False
        
        return False

    def run_single(self) -> bool:
        """
        Run a single execution of the Twitter Manager.
        
        Returns:
            bool: True if post was successful, False otherwise
        """
        logger.info("Starting Twitter Manager single execution")
        
        try:
            success = self.generate_and_post()
            if success:
                logger.info("Successfully posted tweet")
            else:
                logger.warning("Failed to post tweet")
            return success
            
        except Exception as e:
            logger.error(f"Twitter Manager execution failed: {str(e)}")
            raise

    def get_stats(self) -> dict:
        """
        Get posting statistics.
        
        Returns:
            dict: Statistics about posts
        """
        try:
            stats = self.db_manager.get_post_stats()
            logger.info("Retrieved posting statistics")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {str(e)}")
            return {}

def main():
    """Main entry point for the Twitter Manager."""
    try:
        # Add script directory to Python path for absolute imports
        script_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(script_dir))

        logger.info("Starting Twitter Manager application")
        manager = TwitterManager()
        success = manager.run_single()
        
        if success:
            logger.info("Twitter Manager completed successfully")
            sys.exit(0)
        else:
            logger.error("Twitter Manager failed to post")
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()