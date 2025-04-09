# backend/database.py
import psycopg2
from psycopg2.extras import RealDictCursor  # For dict-like row results
from .config import DB_URL

def get_db_connection():
    """Establishes a connection to the Neon.tech Postgres database."""
    try:
        conn = psycopg2.connect(
            DB_URL,
            cursor_factory=RealDictCursor  # Returns rows as dictionaries
        )
        return conn
    except Exception as e:
        raise Exception(f"Failed to connect to database: {str(e)}")

def init_db():
    """Initializes the database by creating required tables if they don't exist."""
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
            raw_id INT REFERENCES raw_data(id),
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
            processed_id INT REFERENCES processed_data(id),
            alert_type VARCHAR(50),
            timestamp TIMESTAMP
        );
    """)
    
    conn.commit()
    conn.close()
    print("Database tables initialized successfully.")

def test_db_connection():
    """Tests the database connection by inserting and retrieving a sample record."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Insert test data
    cur.execute("""
        INSERT INTO raw_data (source, text, timestamp) 
        VALUES (%s, %s, %s) RETURNING id
    """, ("test", "This is a test incident", "2025-04-08 12:00:00"))
    raw_id = cur.fetchone()["id"]
    
    # Insert into processed_data
    cur.execute("""
        INSERT INTO processed_data (raw_id, cleaned_text, sentiment, threat_label, confidence_score)
        VALUES (%s, %s, %s, %s, %s)
    """, (raw_id, "test incident", "neutral", "benign", 0.95))
    
    conn.commit()
    conn.close()
    print("Database test successful.")

if __name__ == "__main__":
    # Run this block to initialize and test the DB
    init_db()
    test_db_connection()