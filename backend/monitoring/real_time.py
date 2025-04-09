# backend/monitoring/real_time.py
import logging
from ..database import get_db_connection
from ..analysis.nlp_analysis import analyze_sentiment
from ..analysis.ml_models import load_models
from ..analysis.anomaly_detection import detect_anomaly

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_real_time(raw_id, text, timestamp):
    """Process a single raw data entry in real-time."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Clean text (assuming clean_text is imported if needed)
        from ..preprocessing.clean_text import clean_text
        cleaned_text = clean_text(text)

        # Sentiment analysis
        sentiment, _ = analyze_sentiment(cleaned_text)

        # Load ML models
        rf, svm, vectorizer = load_models()
        X = vectorizer.transform([cleaned_text])
        threat_label = "threat" if svm.predict(X)[0] == 1 else "benign"
        confidence_score = svm.predict_proba(X)[0][1] if threat_label == "threat" else 1 - svm.predict_proba(X)[0][0]

        # Insert into processed_data
        cur.execute("""
            INSERT INTO processed_data (raw_id, cleaned_text, sentiment, threat_label, confidence_score)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (raw_id, cleaned_text, sentiment, threat_label, confidence_score))
        processed_id = cur.fetchone()["id"]
        conn.commit()

        # Check for anomaly or high-risk content
        if detect_anomaly(cleaned_text) or (threat_label == "threat" and confidence_score > 0.8):
            cur.execute("""
                INSERT INTO alerts (processed_id, alert_type, timestamp)
                VALUES (%s, %s, %s)
            """, (processed_id, "high-risk", timestamp))
            conn.commit()
            

        conn.close()
    except Exception as e:
        logger.error(f"Error in real-time processing: {str(e)}")

if __name__ == "__main__":
    # Test with sample data
    process_real_time(1, "Malware attack in India!", "2025-04-08 12:00:00")