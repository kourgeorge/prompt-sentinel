from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import logging
from datetime import datetime
import sqlite3
import uvicorn

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost:3000",  # Allow requests from your React app
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_FILE = "reports.db"

class ReportData(BaseModel):
    prompt: str
    secrets: List[str]
    sanitized_output: str
    timestamp: str

def get_db_connection():
    """Establishes and returns a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

def create_table_if_not_exists():
    """Creates the reports table if it doesn't exist in the SQLite database."""
    conn = get_db_connection()
    try:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt TEXT,
                    secrets TEXT,
                    sanitized_output TEXT,
                    timestamp TEXT
                );
            """)
            conn.commit()
            logger.info("Reports table created or already exists in SQLite database.")
    except Exception as e:
        logger.error(f"Error creating table: {e}")
    finally:
        conn.close()

def save_report_to_db(data: ReportData):
    """Saves a report to the SQLite database."""
    conn = get_db_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO reports (prompt, secrets, sanitized_output, timestamp)
                VALUES (?, ?, ?, ?)
            """, (data.prompt, str(data.secrets), data.sanitized_output, data.timestamp))
            conn.commit()
            report_id = cursor.lastrowid
            logger.info(f"Saved report with ID: {report_id}")
            cursor.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
            new_report = dict(cursor.fetchone())
            return new_report
    except Exception as e:
        logger.error(f"Error saving report to database: {e}")
        raise HTTPException(status_code=500, detail="Error saving report to database")
    finally:
        conn.close()

def get_all_reports():
    """Retrieves all reports from the database."""
    conn = get_db_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reports")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error retrieving reports from database: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving reports from database")
    finally:
        conn.close()

@app.on_event("startup")
async def startup_event():
    """Ensures the table is created when the app starts."""
    create_table_if_not_exists()

@app.post("/api/report")
async def report_prompt(data: ReportData):
    """
    Receives a report about a prompt, including detected secrets and the sanitized output,
    and saves it to the SQLite database.
    """
    try:
        saved_report = save_report_to_db(data)
        return {"message": "Report saved successfully", "report": saved_report}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/reports")
async def get_reports():
    """Retrieves all reports from the database."""
    try:
        reports = get_all_reports()
        return {"reports": reports}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

def main():
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
