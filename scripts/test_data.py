# scripts/test_data.py
import logging
import sys
import os
import pandas as pd
from datetime import datetime
from backend.database import get_db_connection
from psycopg2.extras import Json

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

TEST_DATA_PATH = "backend/data/cybersecurity_data.csv"

def populate_test_data():
    """Populate the raw_data table with test data from a CSV file at once."""
    try:
        if not os.path.exists(TEST_DATA_PATH):
            logger.error(f"Test data file not found at {TEST_DATA_PATH}. Please create it.")
            raise FileNotFoundError(f"Missing {TEST_DATA_PATH}")
        
        df = pd.read_csv(TEST_DATA_PATH)
        
        conn = get_db_connection()
        cur = conn.cursor()

        # Insert all rows at once
        for _, row in df.iterrows():
            source = row["source"]
            text = row["text"]
            try:
                timestamp = datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
            except (ValueError, TypeError):
                timestamp = datetime.now()
            metadata = (
                {"url": row["url"] or "", "source_name": row["source_name"] or ""} 
                if source == "news" 
                else {"user": "test_user", "id_str": str(row["id"]) or ""}
            )

            cur.execute("""
                INSERT INTO raw_data (source, text, timestamp, metadata)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (source, text, timestamp, Json(metadata)))

        conn.commit()
        print(f"Inserted {len(df)} rows into raw_data at once.")

    except Exception as e:
        logger.error(f"Error populating test data: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        sys.exit(1)
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    populate_test_data()