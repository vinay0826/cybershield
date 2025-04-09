from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import get_db_connection

app = FastAPI(
    title="Cyber Incident Monitoring System",
    description="Real-time monitoring of cyber threats in Indian cyberspace",
    version="0.1.0"
)

# Allow CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def read_root():
    return {"message": "Welcome to the Cyber Incident Monitoring System"}

# Endpoint to fetch incidents with pagination support
@app.get("/incidents")
async def get_incidents(limit: int = 10, offset: int = 0):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT p.*, r.timestamp
            FROM processed_data p
            LEFT JOIN raw_data r ON p.raw_id = r.id
            ORDER BY p.id ASC
            LIMIT %s OFFSET %s
        """, (limit, offset))
        incidents = cur.fetchall()
        conn.close()
        return {"status": "success", "incidents": incidents}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Endpoint to fetch recent alerts
@app.get("/alerts")
async def get_alerts(limit: int = 10, offset: int = 0):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT a.id, a.processed_id, a.alert_type, a.timestamp, p.cleaned_text
            FROM alerts a
            JOIN processed_data p ON a.processed_id = p.id
            ORDER BY a.timestamp ASC
            LIMIT %s OFFSET %s
        """, (limit, offset))
        alerts = cur.fetchall()
        conn.close()
        return alerts
    except Exception as e:
        return {"status": "error", "message": str(e)}


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
