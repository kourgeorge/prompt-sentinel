import warnings
# Suppress SQLAlchemy 2.0 deprecation warnings (we're already using the correct import)
warnings.filterwarnings("ignore", message=".*declarative_base.*")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="sqlalchemy.*")

from fastapi import FastAPI, Request, HTTPException, Depends, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Text, func
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
import hashlib
import os
from pydantic import BaseModel
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from collections import defaultdict, Counter

# Database setup
DATABASE_URL = "sqlite:///./telemetry.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class TelemetryEvent(Base):
    __tablename__ = "telemetry_events"
    
    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(String, index=True)
    session_id = Column(String, index=True)
    prompt = Column(Text)
    secrets = Column(Text)  # JSON string of detected secrets
    sanitized_output = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    secrets_count = Column(Integer, default=0)
    risk_level = Column(String, default="LOW")

class SecurityOfficer(Base):
    __tablename__ = "security_officers"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic Models
class TelemetryReport(BaseModel):
    app_id: str
    session_id: str
    prompt: str
    secrets: List[str]
    sanitized_output: str
    timestamp: str

class LoginForm(BaseModel):
    username: str
    password: str

# Initialize FastAPI app
app = FastAPI(title="Sentinel Telemetry Dashboard", version="1.0.0")

# Templates and Static Files
templates = Jinja2Templates(directory="templates")

# Security
security = HTTPBearer()
FAKE_SECURITY_OFFICERS = {
    "admin": {
        "username": "admin",
        "password": "admin123",  # In real system, this would be hashed
        "role": "security_officer"
    },
    "officer1": {
        "username": "officer1", 
        "password": "secure123",
        "role": "security_officer"
    }
}

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Authentication functions
def verify_credentials(username: str, password: str) -> bool:
    user = FAKE_SECURITY_OFFICERS.get(username)
    if user and user["password"] == password:
        return True
    return False

def create_access_token(username: str) -> str:
    # Simple token creation for demo - just hash the username with a secret
    secret = "demo_secret_key_2024"
    data = f"{username}:{secret}"
    return hashlib.sha256(data.encode()).hexdigest()

def verify_token(token: str) -> Optional[str]:
    # Simple token verification for demo
    secret = "demo_secret_key_2024"
    for username in FAKE_SECURITY_OFFICERS:
        expected_token = hashlib.sha256(f"{username}:{secret}".encode()).hexdigest()
        if token == expected_token:
            return username
    return None

# Security dependency
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    username = verify_token(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return username

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    print(f"🔐 Login attempt: username='{username}', password='{password}'")
    
    if verify_credentials(username, password):
        print(f"✅ Login successful for user: {username}")
        token = create_access_token(username)
        response = RedirectResponse(url="/dashboard", status_code=302)
        response.set_cookie(key="access_token", value=token, httponly=True)
        return response
    else:
        print(f"❌ Login failed for user: {username}")
        print(f"Available users: {list(FAKE_SECURITY_OFFICERS.keys())}")
        return templates.TemplateResponse("login.html", {
            "request": request, 
            "error": "Invalid credentials. Try: admin/admin123 or officer1/secure123"
        })

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    # Get token from cookie
    token = request.cookies.get("access_token")
    if not token or not verify_token(token):
        return RedirectResponse(url="/", status_code=302)
    
    try:
        # Get telemetry statistics
        total_events = db.query(TelemetryEvent).count()
        total_secrets = db.query(func.sum(TelemetryEvent.secrets_count)).scalar() or 0
        unique_apps = db.query(TelemetryEvent.app_id).distinct().count()
        unique_sessions = db.query(TelemetryEvent.session_id).distinct().count()
        
        # Get recent events
        recent_events = db.query(TelemetryEvent).order_by(TelemetryEvent.timestamp.desc()).limit(10).all()
        
        # Get risk distribution
        risk_distribution = db.query(TelemetryEvent.risk_level, func.count(TelemetryEvent.id)).group_by(TelemetryEvent.risk_level).all()
        
        # Create charts with error handling
        try:
            charts = create_dashboard_charts(db)
        except Exception as e:
            print(f"Chart creation error: {e}")
            charts = {}
        
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "total_events": total_events,
            "total_secrets": total_secrets,
            "unique_apps": unique_apps,
            "unique_sessions": unique_sessions,
            "recent_events": recent_events,
            "risk_distribution": risk_distribution,
            "charts": charts,
            "current_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e:
        print(f"Dashboard error: {e}")
        # Return a basic dashboard if there are errors
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "total_events": 0,
            "total_secrets": 0,
            "unique_apps": 0,
            "unique_sessions": 0,
            "recent_events": [],
            "risk_distribution": [],
            "charts": {},
            "current_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        })

def create_dashboard_charts(db: Session) -> Dict[str, str]:
    """Create Plotly charts for the dashboard"""
    charts = {}
    
    # Events over time
    events_over_time = db.query(
        func.date(TelemetryEvent.timestamp).label('date'),
        func.count(TelemetryEvent.id).label('count')
    ).group_by(func.date(TelemetryEvent.timestamp)).all()
    
    if events_over_time:
        dates = [event.date for event in events_over_time]
        counts = [event.count for event in events_over_time]
        
        fig_timeline = go.Figure()
        fig_timeline.add_trace(go.Scatter(
            x=dates, y=counts,
            mode='lines+markers',
            name='Events',
            line=dict(color='#e74c3c', width=3)
        ))
        fig_timeline.update_layout(
            title="Privacy Events Over Time",
            xaxis_title="Date",
            yaxis_title="Number of Events",
            template="plotly_white"
        )
        charts["timeline"] = fig_timeline.to_html(include_plotlyjs=False)
    
    # Top risky apps
    top_apps = db.query(
        TelemetryEvent.app_id,
        func.count(TelemetryEvent.id).label('event_count'),
        func.sum(TelemetryEvent.secrets_count).label('secrets_count')
    ).group_by(TelemetryEvent.app_id).order_by(func.sum(TelemetryEvent.secrets_count).desc()).limit(10).all()
    
    if top_apps:
        app_ids = [app.app_id for app in top_apps]
        secret_counts = [app.secrets_count for app in top_apps]
        
        fig_apps = go.Figure()
        fig_apps.add_trace(go.Bar(
            x=app_ids, y=secret_counts,
            name='Secrets Detected',
            marker_color='#f39c12'
        ))
        fig_apps.update_layout(
            title="Top Applications by Secrets Detected",
            xaxis_title="Application ID",
            yaxis_title="Number of Secrets",
            template="plotly_white"
        )
        charts["top_apps"] = fig_apps.to_html(include_plotlyjs=False)
    
    # Risk levels distribution
    risk_levels = db.query(
        TelemetryEvent.risk_level,
        func.count(TelemetryEvent.id).label('count')
    ).group_by(TelemetryEvent.risk_level).all()
    
    if risk_levels:
        levels = [risk.risk_level for risk in risk_levels]
        counts = [risk.count for risk in risk_levels]
        colors = {'HIGH': '#e74c3c', 'MEDIUM': '#f39c12', 'LOW': '#2ecc71'}
        
        fig_risk = go.Figure()
        fig_risk.add_trace(go.Pie(
            labels=levels, values=counts,
            marker_colors=[colors.get(level, '#3498db') for level in levels],
            hole=0.3
        ))
        fig_risk.update_layout(
            title="Risk Level Distribution",
            template="plotly_white"
        )
        charts["risk_distribution"] = fig_risk.to_html(include_plotlyjs=False)
    
    return charts

def calculate_risk_level(secrets: List[str]) -> str:
    """Calculate risk level based on number and type of secrets"""
    if not secrets:
        return "LOW"
    
    secret_count = len(secrets)
    if secret_count >= 5:
        return "HIGH"
    elif secret_count >= 2:
        return "MEDIUM"
    else:
        return "LOW"

@app.post("/api/report")
async def receive_telemetry(report: TelemetryReport, db: Session = Depends(get_db)):
    """Endpoint to receive telemetry data from Sentinel"""
    
    # Calculate risk level
    risk_level = calculate_risk_level(report.secrets)
    
    # Create telemetry event
    event = TelemetryEvent(
        app_id=report.app_id,
        session_id=report.session_id,
        prompt=report.prompt,
        secrets=json.dumps(report.secrets),
        sanitized_output=report.sanitized_output,
        timestamp=datetime.fromisoformat(report.timestamp.replace('Z', '+00:00')),
        secrets_count=len(report.secrets),
        risk_level=risk_level
    )
    
    db.add(event)
    db.commit()
    
    return {"status": "success", "message": "Telemetry data received"}

@app.get("/api/events")
async def get_events(
    request: Request,
    db: Session = Depends(get_db),
    limit: int = 50,
    offset: int = 0
):
    """Get telemetry events with pagination"""
    token = request.cookies.get("access_token")
    if not token or not verify_token(token):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    events = db.query(TelemetryEvent).order_by(TelemetryEvent.timestamp.desc()).offset(offset).limit(limit).all()
    
    return {
        "events": [
            {
                "id": event.id,
                "app_id": event.app_id,
                "session_id": event.session_id,
                "prompt": event.prompt[:100] + "..." if len(event.prompt) > 100 else event.prompt,
                "secrets": json.loads(event.secrets),
                "secrets_count": event.secrets_count,
                "risk_level": event.risk_level,
                "timestamp": event.timestamp.isoformat()
            }
            for event in events
        ]
    }

@app.get("/events", response_class=HTMLResponse)
async def events_page(request: Request, db: Session = Depends(get_db)):
    """Events listing page"""
    token = request.cookies.get("access_token")
    if not token or not verify_token(token):
        return RedirectResponse(url="/", status_code=302)
    
    events = db.query(TelemetryEvent).order_by(TelemetryEvent.timestamp.desc()).limit(50).all()
    
    return templates.TemplateResponse("events.html", {
        "request": request,
        "events": events
    })

@app.get("/logout")
async def logout():
    """Logout endpoint"""
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("access_token")
    return response

if __name__ == "__main__":
    import uvicorn
    import os
    
    print("🛡️  Sentinel Telemetry Server - UPDATED VERSION")
    print("=" * 60)
    
    port = int(os.getenv("PORT", 8001))  # Default to 8001 instead of 8000
    print(f"� Using port: {port} (default changed from 8000 to 8001)")
    print(f"📊 Dashboard: http://localhost:{port}")
    print("LOGIN CREDENTIALS:")
    print("  admin / admin123")
    print("  officer1 / secure123")
    print("💡 If you see port 8000, you might have an old process running!")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=port)