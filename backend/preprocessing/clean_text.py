# backend/preprocessing/clean_text.py
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

# Initialize stopwords
STOP_WORDS = set(stopwords.words('english'))

def clean_text(text):
    """
    Clean and normalize text data.
    
    Args:
        text (str): Raw text to clean.
    
    Returns:
        str: Cleaned text.
    """
    if not isinstance(text, str) or not text.strip():
        return ""

    # Convert to lowercase
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    # Remove special characters and numbers, keep only letters and spaces
    text = re.sub(r'[^a-z\s]', '', text)
    
    # Tokenize text
    tokens = word_tokenize(text)
    
    # Remove stopwords and short words
    cleaned_tokens = [token for token in tokens if token not in STOP_WORDS and len(token) > 2]
    
    # Join tokens back into a single string
    cleaned_text = ' '.join(cleaned_tokens)
    
    return cleaned_text.strip()

def remove_duplicates(text_list):
    """
    Remove duplicate entries from a list of text strings.
    
    Args:
        text_list (list): List of text strings.
    
    Returns:
        list: List with duplicates removed.
    """
    return list(dict.fromkeys(text_list))

if __name__ == "__main__":
    # Test the cleaning function
    sample_text = "Hacked!!! Visit http://malware.com now #cyberattack INDIA"
    cleaned = clean_text(sample_text)
    print(f"Original: {sample_text}")
    print(f"Cleaned: {cleaned}")
    
    # Test duplicate removal
    sample_list = ["cyber attack", "data breach", "cyber attack"]
    unique_list = remove_duplicates(sample_list)
    print(f"Original list: {sample_list}")
    print(f"Unique list: {unique_list}")