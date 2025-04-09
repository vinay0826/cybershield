@echo off
cd C:\Users\nalag\OneDrive\Desktop\coding\freelance\Cyber_shield
call venv\Scripts\activate
python -c "from backend.database import get_db_connection; conn = get_db_connection(); cur = conn.cursor(); cur.execute('DROP TABLE alerts, processed_data, raw_data CASCADE'); conn.commit(); conn.close()"
python -m scripts.init_db
python -m scripts.test_data
python -m backend.preprocessing.preprocess
python -m backend.analysis.nlp_analysis
python -m backend.analysis.ml_models
python -m backend.analysis.anomaly_detection
uvicorn backend.main:app --reload