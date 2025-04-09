# backend/data_collection/twitter_stream.py
import tweepy
import logging
from datetime import datetime
from ..config import (
    TWITTER_API_KEY,
    TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET,
)
from ..database import get_db_connection

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TwitterStream(tweepy.Stream):
    """Custom Tweepy Stream class to handle real-time Twitter data."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conn = get_db_connection()
        self.cur = self.conn.cursor()

    def on_status(self, status):
        """Handle incoming tweets."""
        try:
            tweet_text = status.text
            timestamp = status.created_at
            source = "twitter"
            metadata = {
                "user": status.user.screen_name,
                "id_str": status.id_str,
                "lang": status.lang
            }

            # Insert raw tweet into raw_data table
            self.cur.execute("""
                INSERT INTO raw_data (source, text, timestamp, metadata)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (source, tweet_text, timestamp, metadata))
            self.conn.commit()
            logger.info(f"Inserted tweet: {tweet_text[:50]}...")
        except Exception as e:
            logger.error(f"Error processing tweet: {str(e)}")
            self.conn.rollback()

    def on_error(self, status_code):
        """Handle streaming errors."""
        logger.error(f"Stream error with status code: {status_code}")
        if status_code == 420:  # Rate limit reached
            return False  # Disconnect stream
        return True

    def on_exception(self, exception):
        """Handle exceptions during streaming."""
        logger.error(f"Stream exception: {str(exception)}")
        return

    def __del__(self):
        """Ensure database connection is closed."""
        try:
            self.conn.close()
            logger.info("Database connection closed.")
        except:
            pass

def start_twitter_stream():
    """Initialize and start the Twitter stream."""
    if not all([TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET]):
        logger.error("Twitter API credentials are missing. Cannot start stream.")
        return

    try:
        # Initialize stream
        stream = TwitterStream(
            TWITTER_API_KEY,
            TWITTER_API_SECRET,
            TWITTER_ACCESS_TOKEN,
            TWITTER_ACCESS_TOKEN_SECRET
        )

        # Define keywords to track (cybersecurity-related, India-focused)
        keywords = [
            "cybersecurity india",
            "cyberattack india",
            "hacked india",
            "malware india",
            "phishing india",
            "#cybercrime",
            "#databreach"
        ]

        # Start streaming
        logger.info("Starting Twitter stream...")
        stream.filter(track=keywords, languages=["en"])
    except Exception as e:
        logger.error(f"Failed to start Twitter stream: {str(e)}")

if __name__ == "__main__":
    start_twitter_stream()