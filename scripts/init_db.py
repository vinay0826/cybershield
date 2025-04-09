# scripts/init_db.py
import logging
from backend.database import get_db_connection  # Import as part of backend package

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_database():
    """Initialize the Postgres database by creating necessary tables."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Create raw_data table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS raw_data (
                id SERIAL PRIMARY KEY,
                source VARCHAR(50),
                text TEXT,
                timestamp TIMESTAMP,
                metadata JSONB
            );
        """)

        # Create processed_data table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS processed_data (
                id SERIAL PRIMARY KEY,
                raw_id INT REFERENCES raw_data(id) ON DELETE CASCADE,
                cleaned_text TEXT,
                sentiment VARCHAR(20),
                threat_label VARCHAR(20),
                confidence_score FLOAT
            );
        """)

        # Create alerts table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id SERIAL PRIMARY KEY,
                processed_id INT REFERENCES processed_data(id) ON DELETE CASCADE,
                alert_type VARCHAR(50),
                timestamp TIMESTAMP
            );
        """)

        conn.commit()
        logger.info("Database tables initialized successfully:")
        logger.info("- raw_data")
        logger.info("- processed_data")
        logger.info("- alerts")

    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        sys.exit(1)
    finally:
        if 'conn' in locals():  # Check if conn was defined
            conn.close()
            logger.info("Database connection closed.")

if __name__ == "__main__":
    initialize_database()