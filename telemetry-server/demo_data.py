#!/usr/bin/env python3
"""
Demo data generator for Sentinel Telemetry Server
This script sends sample telemetry data to test the dashboard functionality.
"""

import requests
import json
import random
import time
from datetime import datetime, timedelta
from typing import List, Dict

# Server configuration
SERVER_URL = "http://localhost:8000"
API_ENDPOINT = f"{SERVER_URL}/api/report"

# Sample data for generating realistic telemetry
SAMPLE_USERS = [
    "user_001", "user_002", "user_003", "user_004", "user_005",
    "finance_team", "hr_department", "dev_team", "marketing_user", "sales_rep"
]

SAMPLE_PROMPTS = [
    "Please help me analyze this customer data: name: John Doe, email: john.doe@company.com, phone: 555-123-4567",
    "I need to process this API key: sk-1234567890abcdef for our integration",
    "Here's my password: MySecretPass123! for the database connection",
    "Can you help me with this SQL query? SELECT * FROM users WHERE password = 'admin123'",
    "I'm sharing this document with confidential employee SSN: 123-45-6789",
    "Please review this configuration: database_url = 'postgresql://user:secret@localhost/db'",
    "My credit card number is 4532 1234 5678 9012, can you help me with billing?",
    "I need to access the system with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "Please analyze this log file with IP addresses: 192.168.1.100, 10.0.0.1",
    "Help me with this email containing PII: customer@domain.com, DOB: 1990-01-01"
]

SAMPLE_SECRETS = [
    ["john.doe@company.com", "555-123-4567"],
    ["sk-1234567890abcdef"],
    ["MySecretPass123!", "admin123"],
    ["admin123"],
    ["123-45-6789"],
    ["postgresql://user:secret@localhost/db", "secret"],
    ["4532 1234 5678 9012"],
    ["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    ["192.168.1.100", "10.0.0.1"],
    ["customer@domain.com", "1990-01-01"]
]

def generate_session_id() -> str:
    """Generate a random session ID"""
    import uuid
    return str(uuid.uuid4())

def generate_telemetry_event() -> Dict:
    """Generate a single telemetry event with random data"""
    index = random.randint(0, len(SAMPLE_PROMPTS) - 1)
    prompt = SAMPLE_PROMPTS[index]
    secrets = SAMPLE_SECRETS[index]
    
    # Generate sanitized output by replacing secrets with placeholders
    sanitized = prompt
    for i, secret in enumerate(secrets):
        sanitized = sanitized.replace(secret, f"__SECRET_{i+1}__")
    
    # Generate timestamp within last 7 days
    now = datetime.now()
    random_time = now - timedelta(
        days=random.randint(0, 7),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59)
    )
    
    return {
        "app_id": random.choice(SAMPLE_USERS),
        "session_id": generate_session_id(),
        "prompt": prompt,
        "secrets": secrets,
        "sanitized_output": sanitized,
        "timestamp": random_time.isoformat()
    }

def send_telemetry_event(event: Dict) -> bool:
    """Send a single telemetry event to the server"""
    try:
        response = requests.post(API_ENDPOINT, json=event)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error sending event: {e}")
        return False

def generate_and_send_events(num_events: int = 50):
    """Generate and send multiple telemetry events"""
    print(f"Generating {num_events} sample telemetry events...")
    
    successful = 0
    failed = 0
    
    for i in range(num_events):
        event = generate_telemetry_event()
        
        print(f"Sending event {i+1}/{num_events}: {event['app_id']} - {len(event['secrets'])} secrets")
        
        if send_telemetry_event(event):
            successful += 1
        else:
            failed += 1
        
        # Add small delay to simulate real-time events
        time.sleep(0.1)
    
    print(f"\nDemo data generation complete!")
    print(f"Successfully sent: {successful} events")
    print(f"Failed to send: {failed} events")
    print(f"\nYou can now view the dashboard at: {SERVER_URL}/dashboard")

def check_server_health():
    """Check if the telemetry server is running"""
    try:
        response = requests.get(f"{SERVER_URL}/")
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

if __name__ == "__main__":
    print("Sentinel Telemetry Server - Demo Data Generator")
    print("=" * 50)
    
    # Check if server is running
    if not check_server_health():
        print(f"❌ Server is not running at {SERVER_URL}")
        print("Please start the server first with: python main.py")
        exit(1)
    
    print(f"✅ Server is running at {SERVER_URL}")
    
    # Generate demo data
    generate_and_send_events(50)
    
    print("\n" + "=" * 50)
    print("Demo credentials for the dashboard:")
    print("Admin: admin / admin123")
    print("Officer: officer1 / secure123")
    print("=" * 50)