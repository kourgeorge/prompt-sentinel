from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import logging
import sqlite3
import uvicorn
import psycopg2
import os
from psycopg2.extras import RealDictCursor

app = FastAPI()

# Database configuration
DATABASE_TYPE = os.environ.get("DATABASE_TYPE", "sqlite")  # Default to SQLite
SQLITE_DATABASE_FILE = os.environ.get("SQLITE_DATABASE_FILE", "reports.db")
POSTGRES_DATABASE_URL = os.environ.get("POSTGRES_DATABASE_URL", "postgresql://reports_o1oj_user:ZzR6nOYqU8xoz6YIdfT55ESoXoFgui4f@dpg-cvu2cgruibrs73eho9ug-a/reports_o1oj")

# CORS configuration
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

class ReportData(BaseModel):
    app_id: str
    session_id: str
    prompt: str
    secrets: List[str]
    sanitized_output: str
    timestamp: str

def get_db_connection():    
    if DATABASE_TYPE == "sqlite":
        conn = sqlite3.connect(SQLITE_DATABASE_FILE)
        conn.row_factory = sqlite3.Row  # Access columns by name
        return conn
    elif DATABASE_TYPE == "postgresql":
        try:
            conn = psycopg2.connect(POSTGRES_DATABASE_URL)
            return conn
        except Exception as e:
            logger.error(f"Error connecting to PostgreSQL database: {e}")
            raise
    else:
        raise ValueError(f"Invalid DATABASE_TYPE: {DATABASE_TYPE}")

def create_table_if_not_exists():
    conn = get_db_connection()    
    try:
        if DATABASE_TYPE == "sqlite":
            with conn:
                conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='reports'")
                table_exists = conn.fetchone() is not None
                if not table_exists:
                    conn.execute("""
                        CREATE TABLE reports (
                            app_id TEXT, 
                            session_id TEXT,
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            prompt TEXT,
                            secrets TEXT,
                            sanitized_output TEXT,
                            timestamp TEXT
                        );
                    """)
                    conn.commit()
                    logger.info("Reports table created in SQLite database.")
                else:
                    logger.info("Reports table already exists in SQLite database.")
        elif DATABASE_TYPE == "postgresql":
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'reports');")
            table_exists = cursor.fetchone()['exists']
            if not table_exists:
                cursor.execute("""
                    CREATE TABLE reports (
                        id SERIAL PRIMARY KEY,
                        app_id TEXT,
                        session_id TEXT,
                        prompt TEXT,
                        secrets TEXT,
                        sanitized_output TEXT,
                        timestamp TEXT
                    );
                """)
                conn.commit()
                logger.info("Reports table created in PostgreSQL database.")
            else:
                logger.info("Reports table already exists in PostgreSQL database.")
    except Exception as e:
        logger.error(f"Error creating or checking for table: {e}")
    finally:
       conn.close()

def save_report_to_db(data: ReportData):
    """Saves a report to the SQLite database."""
    conn = get_db_connection()
    try:
        with conn:
            cursor = conn.cursor()
            if DATABASE_TYPE == "sqlite":
                cursor.execute("""
                    INSERT INTO reports (app_id, session_id, prompt, secrets, sanitized_output, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (data.app_id, data.session_id, data.prompt, str(data.secrets), data.sanitized_output, data.timestamp))
                report_id = cursor.lastrowid
                cursor.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
                new_report = dict(cursor.fetchone())
            elif DATABASE_TYPE == "postgresql":
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute("""
                    INSERT INTO reports (app_id, session_id, prompt, secrets, sanitized_output, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;
                """, (data.app_id, data.session_id, data.prompt, str(data.secrets), data.sanitized_output, data.timestamp))
                report_id = cursor.fetchone()['id']
                cursor.execute("SELECT * FROM reports WHERE id = %s", (report_id,))
                new_report = cursor.fetchone()
            
            conn.commit()
            logger.info(f"Saved report with ID: {report_id}")
            
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
            if DATABASE_TYPE == "sqlite":
                cursor.execute("SELECT * FROM reports")
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
            elif DATABASE_TYPE == "postgresql":
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute("SELECT * FROM reports")
                rows = cursor.fetchall()
                return rows

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
    uvicorn.run("main:app", host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()