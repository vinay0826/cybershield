# backend/config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration
DB_URL = os.getenv("DB_URL")  # Neon.tech Postgres connection string

# Twitter API credentials
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

# News API key
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Validate essential configs
if not DB_URL:
    raise ValueError("DB_URL environment variable is not set. Please set it in .env file.")
if not all([TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET]):
    print("Warning: Twitter API credentials missing. Twitter streaming will not work.")
if not NEWS_API_KEY:
    print("Warning: NEWS_API_KEY missing. News fetching will not work.")