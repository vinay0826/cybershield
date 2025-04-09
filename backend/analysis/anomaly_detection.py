# backend/analysis/anomaly_detection.py
import logging
import re
from ..database import get_db_connection

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple list of suspicious keywords/regex patterns
SUSPICIOUS_PATTERNS = [
    r'malware', r'phish', r'hack', r'virus', r'exploit',
    r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'  # URLs
]

def detect_anomaly(text):
    """
    Detect anomalies in text based on suspicious patterns.
    
    Args:
        text (str): Text to analyze.
    
    Returns:
        bool: True if anomaly detected, False otherwise.
    """
    if not text or not isinstance(text, str):
        return False
    
    text = text.lower()
    return any(re.search(pattern, text) for pattern in SUSPICIOUS_PATTERNS)

def check_anomalies_batch(limit=100):
    """Check for anomalies in a batch of processed_data records."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Fetch records
        cur.execute("""
            SELECT id, cleaned_text
            FROM processed_data
            LIMIT %s
        """, (limit,))
        records = cur.fetchall()

        if not records:
            logger.info("No records to check for anomalies.")
            return

        anomalies = []
        for record in records:
            processed_id = record["id"]
            text = record["cleaned_text"]
            if detect_anomaly(text):
                anomalies.append(processed_id)
                logger.info(f"Anomaly detected in processed_id {processed_id}: {text[:50]}...")

        conn.close()
        return anomalies
    except Exception as e:
        logger.error(f"Error in check_anomalies_batch: {str(e)}")
        return []

if __name__ == "__main__":
    anomalies = check_anomalies_batch(limit=5)
    print(f"Detected anomalies in processed_ids: {anomalies}")