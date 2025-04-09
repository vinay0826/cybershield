# backend/analysis/ml_models.py
import logging
import pickle
import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from ..database import get_db_connection
from ..monitoring.alerts import generate_alert

logging.basicConfig(level=logging.WARNING)  # Changed to WARNING
logger = logging.getLogger(__name__)

MODEL_DIR = "backend/models"
RF_MODEL_PATH = os.path.join(MODEL_DIR, "rf_model.pkl")
SVM_MODEL_PATH = os.path.join(MODEL_DIR, "svm_model.pkl")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "vectorizer.pkl")
DATA_PATH = "backend/data/cybersecurity_training_data.csv"

def train_models():
    if not os.path.exists(DATA_PATH):
        logger.error(f"Training data file not found at {DATA_PATH}. Please create it.")
        raise FileNotFoundError(f"Missing {DATA_PATH}")
    
    df = pd.read_csv(DATA_PATH)
    texts = df["text"].tolist()
    labels = df["label"].tolist()

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(texts)

    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X, labels)

    svm = SVC(probability=True, kernel='linear', random_state=42)
    svm.fit(X, labels)

    os.makedirs(MODEL_DIR, exist_ok=True)
    with open(RF_MODEL_PATH, "wb") as f:
        pickle.dump(rf, f)
    with open(SVM_MODEL_PATH, "wb") as f:
        pickle.dump(svm, f)
    with open(VECTORIZER_PATH, "wb") as f:
        pickle.dump(vectorizer, f)
    
    print("Models trained and saved using CSV data.")  # Changed to print()

def load_models():
    if not all(os.path.exists(p) for p in [RF_MODEL_PATH, SVM_MODEL_PATH, VECTORIZER_PATH]):
        logger.info("Models not found. Training with CSV data...")
        train_models()
    
    with open(RF_MODEL_PATH, "rb") as f:
        rf = pickle.load(f)
    with open(SVM_MODEL_PATH, "rb") as f:
        svm = pickle.load(f)
    with open(VECTORIZER_PATH, "rb") as f:
        vectorizer = pickle.load(f)
    return rf, svm, vectorizer


def classify_threats_batch(limit=300):  # Changed to process all 300 rows
    try:
        rf, svm, vectorizer = load_models()
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, cleaned_text
            FROM processed_data
            WHERE threat_label = 'unknown'
            LIMIT %s
        """, (limit,))
        records = cur.fetchall()

        if not records:
            logger.warning("No records need threat classification.")
            return

        for record in records:
            processed_id = record["id"]
            text = record["cleaned_text"]
            
            if not text:
                logger.warning(f"Skipping processed_id {processed_id}: cleaned_text is empty.")
                continue
            
            X = vectorizer.transform([text])
            threat_label = "threat" if svm.predict(X)[0] == 1 else "benign"
            confidence_score = svm.predict_proba(X)[0][1] if threat_label == "threat" else 1 - svm.predict_proba(X)[0][0]
            
            cur.execute("""
                UPDATE processed_data
                SET threat_label = %s, confidence_score = %s
                WHERE id = %s
            """, (threat_label, float(confidence_score), processed_id))
            conn.commit()

            # Generate alert if threat with high confidence
            if threat_label == "threat" and confidence_score > 0.75:
                generate_alert(processed_id, "high-risk")

        conn.close()
        print(f"Classified threats for {len(records)} records.")

    except Exception as e:
        logger.error(f"Error in classify_threats_batch: {str(e)}")
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    classify_threats_batch(limit=300)
