# backend/preprocessing/preprocess.py
import logging
import nltk
from ..database import get_db_connection
from .clean_text import clean_text

logging.basicConfig(level=logging.WARNING)  # Changed to WARNING
logger = logging.getLogger(__name__)

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    logger.info("Downloading NLTK punkt_tab resource...")
    nltk.download('punkt_tab')

def preprocess_batch(batch_size=100):
    """Preprocess a batch of raw_data records."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, text
            FROM raw_data
            WHERE id NOT IN (SELECT raw_id FROM processed_data WHERE raw_id IS NOT NULL)
            LIMIT %s
        """, (batch_size,))
        raw_records = cur.fetchall()

        if not raw_records:
            logger.warning("No new raw data to preprocess.")  # Changed to warning
            return

        for record in raw_records:
            raw_id = record["id"]
            text = record["text"]
            cleaned_text = clean_text(text)
            
            cur.execute("""
                INSERT INTO processed_data (raw_id, cleaned_text, sentiment, threat_label, confidence_score)
                VALUES (%s, %s, %s, %s, %s)
            """, (raw_id, cleaned_text, "unknown", "unknown", 0.0))
            

        conn.commit()
        print(f"Preprocessed {len(raw_records)} records.")  # Summary with print()

    except Exception as e:
        logger.error(f"Error in preprocess_batch: {str(e)}")
        conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    preprocess_batch()