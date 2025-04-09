# backend/monitoring/alerts.py
import logging
from ..database import get_db_connection

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_alert(processed_id, alert_type):
    """Generate and log an alert."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO alerts (processed_id, alert_type, timestamp)
            VALUES (%s, %s, CURRENT_TIMESTAMP)
        """, (processed_id, alert_type))
        conn.commit()

       
        cur.execute("""
            SELECT cleaned_text, threat_label, confidence_score
            FROM processed_data
            WHERE id = %s
        """, (processed_id,))
        data = cur.fetchone()

        conn.close()
    except Exception as e:
        logger.error(f"Error generating alert: {str(e)}")

def fetch_recent_alerts(limit=10):
    """Fetch recent alerts from the database."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT a.id, a.processed_id, a.alert_type, a.timestamp, p.cleaned_text
            FROM alerts a
            JOIN processed_data p ON a.processed_id = p.id
            ORDER BY a.timestamp DESC
            LIMIT %s
        """, (limit,))
        alerts = cur.fetchall()
        conn.close()
        return [dict(alert) for alert in alerts]
    except Exception as e:
        logger.error(f"Error fetching alerts: {str(e)}")
        return []

if __name__ == "__main__":
    generate_alert(1, "test-alert")
    alerts = fetch_recent_alerts()
    print(alerts)