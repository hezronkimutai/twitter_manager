"""Content generator for Twitter posts with advanced features and analytics."""
import random
from typing import Optional, Dict, List, Tuple
from collections import Counter, defaultdict
import re
import json
import datetime
from pathlib import Path
import hashlib
import string
from dataclasses import dataclass
import logging
import math
import sys
from os.path import dirname, abspath, join

# Add the project root to Python path to enable importing from data directory
project_root = dirname(dirname(abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TweetMetrics:
    """Dataclass for storing tweet metrics."""
    length: int
    hashtag_count: int
    mention_count: int
    url_count: int
    emoji_count: int
    sentiment_score: float
    readability_score: float
    topic: str
    generated_at: datetime.datetime

class ContentStatistics:
    """Handles statistical analysis of generated content."""
    
    def __init__(self):
        """Initialize statistics tracker."""
        self.total_generated = 0
        self.topic_distribution = Counter()
        self.hourly_stats = defaultdict(int)
        self.length_distribution = []
        self.success_rate = 0.0
        self.last_reset = datetime.datetime.now()
    
    def update(self, tweet: str, topic: str, success: bool):
        """Update statistics with new tweet data."""
        self.total_generated += 1
        self.topic_distribution[topic] += 1
        hour = datetime.datetime.now().hour
        self.hourly_stats[hour] += 1
        self.length_distribution.append(len(tweet))
        
        if success:
            self.success_rate = (
                (self.success_rate * (self.total_generated - 1) + 1) / 
                self.total_generated
            )
        else:
            self.success_rate = (
                (self.success_rate * (self.total_generated - 1)) / 
                self.total_generated
            )
    
    def get_summary(self) -> Dict:
        """Get statistical summary."""
        return {
            "total_generated": self.total_generated,
            "topic_distribution": dict(self.topic_distribution),
            "hourly_stats": dict(self.hourly_stats),
            "avg_length": sum(self.length_distribution) / len(self.length_distribution) if self.length_distribution else 0,
            "success_rate": self.success_rate,
            "time_since_reset": (datetime.datetime.now() - self.last_reset).seconds
        }
    
    def reset(self):
        """Reset statistics."""
        self.__init__()

class ContentAnalyzer:
    """Analyzes content for various metrics and quality factors."""
    
    EMOJI_PATTERN = re.compile("[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]")
    URL_PATTERN = re.compile(r'https?://\S+|www\.\S+')
    MENTION_PATTERN = re.compile(r'@\w+')
    HASHTAG_PATTERN = re.compile(r'#\w+')
    
    @staticmethod
    def count_emojis(text: str) -> int:
        """Count emojis in text."""
        return len(ContentAnalyzer.EMOJI_PATTERN.findall(text))
    
    @staticmethod
    def count_urls(text: str) -> int:
        """Count URLs in text."""
        return len(ContentAnalyzer.URL_PATTERN.findall(text))
    
    @staticmethod
    def count_mentions(text: str) -> int:
        """Count mentions in text."""
        return len(ContentAnalyzer.MENTION_PATTERN.findall(text))
    
    @staticmethod
    def count_hashtags(text: str) -> int:
        """Count hashtags in text."""
        return len(ContentAnalyzer.HASHTAG_PATTERN.findall(text))
    
    @staticmethod
    def calculate_readability(text: str) -> float:
        """Calculate readability score."""
        words = text.split()
        if not words:
            return 0.0
        avg_word_length = sum(len(word) for word in words) / len(words)
        sentences = text.count('.') + text.count('!') + text.count('?')
        sentences = max(1, sentences)
        return (4.71 * avg_word_length + 0.5 * (len(words) / sentences) - 21.43)
    
    @classmethod
    def analyze_tweet(cls, tweet: str, topic: str) -> TweetMetrics:
        """Analyze tweet and return metrics."""
        return TweetMetrics(
            length=len(tweet),
            hashtag_count=cls.count_hashtags(tweet),
            mention_count=cls.count_mentions(tweet),
            url_count=cls.count_urls(tweet),
            emoji_count=cls.count_emojis(tweet),
            sentiment_score=cls.calculate_sentiment(tweet),
            readability_score=cls.calculate_readability(tweet),
            topic=topic,
            generated_at=datetime.datetime.now()
        )
    
    @staticmethod
    def calculate_sentiment(text: str) -> float:
        """Calculate simple sentiment score."""
        positive_words = {
            'great', 'good', 'awesome', 'excellent', 'best', 'improve', 
            'efficient', 'optimize', 'helpful', 'useful', 'powerful',
            'simple', 'clean', 'fast', 'reliable', 'robust', 'secure'
        }
        negative_words = {
            'bad', 'worst', 'poor', 'avoid', 'complex', 'difficult', 
            'problem', 'issue', 'bug', 'error', 'crash', 'slow',
            'complicated', 'unreliable', 'insecure', 'vulnerable'
        }
        
        words = text.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        if not words:
            return 0.0
            
        return (positive_count - negative_count) / len(words)

class ContentFilter:
    """Filters and validates content before posting."""
    
    def __init__(self):
        """Initialize content filter."""
        self.blacklist_words = {
            'spam', 'abuse', 'hack', 'crack', 'illegal', 'malware',
            'virus', 'exploit', 'nsfw', 'scam', 'fraud'
        }
    
    def contains_blacklisted_words(self, text: str) -> bool:
        """Check if text contains blacklisted words."""
        words = set(text.lower().split())
        return bool(words.intersection(self.blacklist_words))
    
    def check_repetition(self, text: str) -> bool:
        """Check for excessive word repetition."""
        words = text.lower().split()
        word_counts = Counter(words)
        max_count = max(word_counts.values()) if word_counts else 0
        return max_count <= 3
    
    def check_length_distribution(self, text: str) -> bool:
        """Check if text has good length distribution."""
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        if not sentences:
            return False
        
        lengths = [len(s) for s in sentences]
        avg_length = sum(lengths) / len(lengths)
        variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)
        return variance < 500  # Arbitrary threshold
    
    def is_content_valid(self, text: str) -> Tuple[bool, str]:
        """
        Validate content using multiple criteria.
        Returns (is_valid, reason) tuple.
        """
        if self.contains_blacklisted_words(text):
            return False, "Contains blacklisted words"
            
        if not self.check_repetition(text):
            return False, "Contains excessive repetition"
            
        if not self.check_length_distribution(text):
            return False, "Poor sentence length distribution"
            
        return True, "Content is valid"

class ContentGenerator:
    """Generates content for Twitter posts."""
    
    def __init__(self):
        """Initialize the content generator with tips from programming_tips.py."""
        # Import tips from programming_tips.py
        try:
            from data.programming_tips import tips
            self.tips = tips
        except ImportError:
            logger.error("Failed to import tips from programming_tips.py")
            # Fallback to a minimal set of tips if import fails
            self.tips = {
                "Programming": [
                    "Write clean, maintainable code",
                    "Use proper error handling",
                    "Test your code thoroughly"
                ]
            }
        self.stats = ContentStatistics()
        self.analyzer = ContentAnalyzer()
        self.filter = ContentFilter()
        self.cache = {}
        self.last_topics = []
        self.MAX_CACHE_SIZE = 1000
        self.CACHE_EXPIRY = datetime.timedelta(hours=24)

    def generate_tweet(self) -> str:
        """Generate a tweet by selecting a random topic and tip."""
        topic = self._select_topic()
        tip = random.choice(self.tips[topic])
        tweet = f"🔥 {topic} Tip:\n\n{tip} #coding #programming #tech"
        
        self._update_metrics(tweet, topic)
        return tweet

    def _select_topic(self) -> str:
        """Select topic while avoiding recent repeats."""
        available_topics = list(set(self.tips.keys()) - set(self.last_topics[-3:]))
        if not available_topics:
            available_topics = list(self.tips.keys())
            
        topic = random.choice(available_topics)
        self.last_topics.append(topic)
        if len(self.last_topics) > 10:
            self.last_topics.pop(0)
        return topic

    def _update_metrics(self, tweet: str, topic: str):
        """Update metrics for generated tweet."""
        metrics = self.analyzer.analyze_tweet(tweet, topic)
        
        # Clean cache if needed
        if len(self.cache) >= self.MAX_CACHE_SIZE:
            self._clean_cache()
        
        # Add to cache
        tweet_hash = hashlib.md5(tweet.encode()).hexdigest()
        self.cache[tweet_hash] = {
            'tweet': tweet,
            'topic': topic,
            'timestamp': datetime.datetime.now(),
            'metrics': metrics
        }
        
        # Update statistics
        self.stats.update(tweet, topic, True)

    def _clean_cache(self):
        """Clean expired entries from cache."""
        now = datetime.datetime.now()
        self.cache = {
            k: v for k, v in self.cache.items()
            if now - v['timestamp'] < self.CACHE_EXPIRY
        }

    def get_analytics(self) -> Dict:
        """Get comprehensive analytics about generated content."""
        return {
            'statistics': self.stats.get_summary(),
            'cache_size': len(self.cache),
            'recent_topics': self.last_topics,
            'topic_count': len(self.tips),
            'total_tips': sum(len(tips) for tips in self.tips.values())
        }

    def is_content_appropriate(self, content: str) -> bool:
        """Check if the content is appropriate for posting."""
        if not (10 <= len(content) <= 280):
            return False
            
        is_valid, _ = self.filter.is_content_valid(content)
        if not is_valid:
            return False
            
        metrics = self.analyzer.analyze_tweet(content, "unknown")
        if metrics.sentiment_score < -0.2:
            return False
            
        if metrics.readability_score > 50:
            return False
            
        return True

    def export_analytics(self, filepath: Optional[str] = None) -> None:
        """Export analytics data to JSON file."""
        analytics = self.get_analytics()
        analytics['export_time'] = datetime.datetime.now().isoformat()
        
        if filepath is None:
            filepath = f"analytics_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
        try:
            with open(filepath, 'w') as f:
                json.dump(analytics, f, indent=2)
            logger.info(f"Analytics exported to {filepath}")
        except Exception as e:
            logger.error(f"Failed to export analytics: {e}")