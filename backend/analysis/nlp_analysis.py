# backend/analysis/nlp_analysis.py
import logging
from textblob import TextBlob
from ..database import get_db_connection

logging.basicConfig(level=logging.WARNING)  # Changed to WARNING
logger = logging.getLogger(__name__)

def analyze_sentiment(text):
    if not text or not isinstance(text, str):
        return "neutral", 0.0
    
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    
    if polarity > 0:
        sentiment = "positive"
    elif polarity < 0:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    
    return sentiment, polarity

def update_sentiment_batch(limit=100):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, cleaned_text
            FROM processed_data
            WHERE sentiment = 'unknown'
            LIMIT %s
        """, (limit,))
        records = cur.fetchall()

        if not records:
            logger.warning("No records need sentiment analysis.")  # Changed to warning
            return

        for record in records:
            processed_id = record["id"]
            text = record["cleaned_text"]
            
            sentiment, _ = analyze_sentiment(text)
            
            try:
                cur.execute("""
                    UPDATE processed_data
                    SET sentiment = %s
                    WHERE id = %s
                """, (sentiment, processed_id))
                conn.commit()
                # Removed individual logger.info()
            except Exception as e:
                logger.error(f"Error updating sentiment for processed_id {processed_id}: {str(e)}")
                conn.rollback()

        conn.close()
        print(f"Processed sentiment for {len(records)} records.")  # Summary with print()

    except Exception as e:
        logger.error(f"Error in update_sentiment_batch: {str(e)}")

if __name__ == "__main__":
    update_sentiment_batch(limit=300)
