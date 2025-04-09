# backend/data_collection/news_fetch.py
import requests
import logging
from datetime import datetime
from ..config import NEWS_API_KEY
from ..database import get_db_connection
from psycopg2.extras import Json

logging.basicConfig(level=logging.WARNING)  # Changed to WARNING
logger = logging.getLogger(__name__)

def fetch_news():
    if not NEWS_API_KEY:
        logger.error("NEWS_API_KEY is missing. Cannot fetch news.")
        return

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": "cybersecurity india OR cyberattack india OR malware india OR phishing india OR data breach india -sports -entertainment",
        "language": "en",
        "sortBy": "relevancy",
        "apiKey": NEWS_API_KEY,
        "pageSize": 20
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        news_data = response.json()

        if news_data.get("status") != "ok":
            logger.error(f"News API error: {news_data.get('message')}")
            return

        articles = news_data.get("articles", [])
        if not articles:
            logger.warning("No news articles found.")
            return

        conn = get_db_connection()
        cur = conn.cursor()

        inserted_count = 0
        for article in articles:
            title = article.get("title", "")
            description = article.get("description", "") or ""
            text = f"{title} {description}".strip()
            published_at = article.get("publishedAt")
            timestamp = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ") if published_at else datetime.now()
            source = article.get("source", {}).get("name", "unknown")
            metadata = {
                "url": article.get("url", ""),
                "author": article.get("author", ""),
                "published_at": published_at
            }

            try:
                cur.execute("""
                    INSERT INTO raw_data (source, text, timestamp, metadata)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """, (source, text, timestamp, Json(metadata)))
                conn.commit()
                inserted_count += 1
                
            except Exception as e:
                logger.error(f"Error inserting article: {str(e)}")
                conn.rollback()

        conn.close()
        print(f"Inserted {inserted_count} news articles.")  # Summary with print()

    except requests.RequestException as e:
        logger.error(f"Failed to fetch news: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in fetch_news: {str(e)}")

if __name__ == "__main__":
    fetch_news()