"""Configuration settings for the Twitter Manager."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Twitter API Configuration
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
# Client_secret = yh9hgte36OjheZu9EY00CUmJhwVczfgsIjgJ3AH4fDbClQZzsB
# Database Configuration
DB_PATH = BASE_DIR / "data" / "twitter.db"

# Logging Configuration
LOG_PATH = BASE_DIR / "logs" / "twitter_manager.log"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"

# Content Generation Configuration
PROMPT_TEMPLATE = """Generate a concise and informative tweet about {topic} that would be useful for developers.
The tweet should be technical but accessible, and include practical tips or insights.
Keep it under 280 characters."""

TOPICS = [
    "Python programming",
    "JavaScript best practices",
    "Software architecture",
    "Clean code principles",
    "Web development",
    "API design",
    "DevOps practices",
    "Database optimization",
    "Security best practices",
    "Code testing strategies"
]

# Scheduling Configuration
POST_INTERVAL_SECONDS = 10  # Post every 10 seconds
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 60

# Rate Limiting
MAX_TWEETS_PER_DAY = 50  # Maximum Twitter API limit
RATE_LIMIT_BUFFER = 0.9  # Buffer to stay under rate limits

def validate_config():
    """Validate that all required configuration variables are set."""
    required_vars = [
        "TWITTER_API_KEY",
        "TWITTER_API_SECRET",
        "TWITTER_ACCESS_TOKEN",
        "TWITTER_ACCESS_TOKEN_SECRET",
        "BEARER_TOKEN"
    ]
    
    missing_vars = [var for var in required_vars if not globals().get(var)]
    
    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}\n"
            "Please check your .env file and ensure all required variables are set."
        )

    # Create necessary directories if they don't exist
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)