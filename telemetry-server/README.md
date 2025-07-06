# Sentinel Telemetry Dashboard

A comprehensive security dashboard for monitoring and analyzing privacy data usage from Sentinel-protected applications.

## 🚀 Features

- **Real-time Privacy Monitoring**: Track sensitive data detection events in real-time
- **Advanced Analytics**: Visualize privacy events with interactive charts and graphs
- **Risk Assessment**: Automatic risk level calculation based on detected secrets
- **User & Session Tracking**: Monitor which users and sessions are sending private data
- **Security Dashboard**: Clean, professional interface for security officers
- **Event Details**: Deep dive into specific privacy events with full context

## 📋 Requirements

- Python 3.7+
- FastAPI
- SQLAlchemy
- SQLite (for database)
- Plotly (for charts)
- Bootstrap 5 (for UI)

## 🛠️ Installation

1. **Clone or extract the telemetry server files**
   ```bash
   cd telemetry-server
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the server**
   ```bash
   python main.py
   ```

   The server will start on `http://localhost:8000`

## 🔐 Authentication

The system includes fake authentication for demo purposes:

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Security Officer |
| officer1 | secure123 | Security Officer |

## 🖥️ Dashboard Features

### Main Dashboard
- **Live Statistics**: Total events, secrets detected, unique users, active sessions
- **Timeline Chart**: Privacy events over time
- **Risk Distribution**: Pie chart showing risk levels
- **Top Risky Applications**: Bar chart of applications with most secrets
- **Recent Events**: Latest privacy events with quick preview

### Events Page
- **Detailed Event Listing**: Complete table of all privacy events
- **Event Details Modal**: Click to view full event information
- **Filtering Options**: Filter by risk level, user ID, date range
- **Export Capabilities**: Ready for data export features

## 📊 API Endpoints

### POST `/api/report`
Receives telemetry data from Sentinel instances.

**Request Body:**
```json
{
  "app_id": "user_001",
  "session_id": "uuid4-session-id",
  "prompt": "Original prompt with secrets",
  "secrets": ["secret1", "secret2"],
  "sanitized_output": "Sanitized prompt with __SECRET_1__ tokens",
  "timestamp": "2023-12-01T10:00:00Z"
}
```

### GET `/api/events`
Retrieves privacy events (requires authentication).

**Response:**
```json
{
  "events": [
    {
      "id": 1,
      "app_id": "user_001",
      "session_id": "uuid4-session-id",
      "secrets_count": 2,
      "risk_level": "HIGH",
      "timestamp": "2023-12-01T10:00:00Z"
    }
  ]
}
```

## 🧪 Testing with Demo Data

1. **Start the server**
   ```bash
   python main.py
   ```

2. **Generate sample data** (in another terminal)
   ```bash
   python demo_data.py
   ```

3. **Access the dashboard**
   - Open `http://localhost:8000`
   - Login with demo credentials
   - Explore the dashboard with generated data

## 🔧 Configuration

### Environment Variables
You can configure the server using these environment variables:

```bash
# Database URL (default: sqlite:///./telemetry.db)
DATABASE_URL="sqlite:///./telemetry.db"

# Server host and port
HOST="0.0.0.0"
PORT=8000
```

### Sentinel Configuration
To connect your Sentinel instances to this dashboard, configure them with:

```python
# In your Sentinel configuration
PS_SERVER_URL="http://localhost:8000"
PS_APP_ID="your-app-identifier"
```

## 🏗️ Architecture

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│                     │    │                     │    │                     │
│  Sentinel Instance  │───▶│  Telemetry Server   │───▶│  Security Dashboard │
│                     │    │                     │    │                     │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
                                       │
                                       ▼
                             ┌─────────────────────┐
                             │                     │
                             │   SQLite Database   │
                             │                     │
                             └─────────────────────┘
```

## 📈 Risk Assessment

The system automatically calculates risk levels based on detected secrets:

- **HIGH**: 5+ secrets detected
- **MEDIUM**: 2-4 secrets detected
- **LOW**: 1 secret detected

## 🔒 Security Considerations

This is a **demo/MVP system** with the following security limitations:

1. **Authentication**: Uses simple fake authentication (replace with proper OAuth/SAML)
2. **Data Storage**: Stores sensitive data in plain text (implement encryption)
3. **API Security**: No rate limiting or API key validation
4. **HTTPS**: Not configured (enable SSL/TLS for production)

## 🚀 Production Deployment

For production use, consider:

1. **Database**: Replace SQLite with PostgreSQL/MySQL
2. **Authentication**: Implement proper RBAC with OAuth2/SAML
3. **Encryption**: Encrypt sensitive data at rest
4. **Monitoring**: Add proper logging and monitoring
5. **Scaling**: Use Docker/Kubernetes for scaling
6. **Security**: Add rate limiting, input validation, CSRF protection

## 📝 Development

### Adding New Features

1. **New API Endpoints**: Add to `main.py`
2. **New UI Pages**: Create templates in `templates/`
3. **Database Changes**: Update models in `main.py`
4. **Styling**: Modify CSS in `base.html`

### Database Schema

```sql
CREATE TABLE telemetry_events (
    id INTEGER PRIMARY KEY,
    app_id VARCHAR,
    session_id VARCHAR,
    prompt TEXT,
    secrets TEXT,  -- JSON array
    sanitized_output TEXT,
    timestamp DATETIME,
    secrets_count INTEGER,
    risk_level VARCHAR
);
```

## 🐛 Troubleshooting

### Common Issues

1. **Server won't start**: Check if port 8000 is available
2. **Database errors**: Ensure write permissions in the directory
3. **Demo data fails**: Verify server is running before generating data
4. **Charts not loading**: Check internet connection for CDN resources

### Logs

Check the console output for detailed error messages and request logs.

## 📧 Support

This is a demo system. For production use, consider proper enterprise security solutions.

## 🔄 Integration with Sentinel

To integrate with the existing Sentinel system, the `SessionContext.report_to_server()` method already sends telemetry data to this dashboard. Just configure:

```python
# In your application using Sentinel
os.environ["PS_SERVER_URL"] = "http://localhost:8000"
os.environ["PS_APP_ID"] = "your-app-name"
```

The Sentinel library will automatically start sending telemetry data to this dashboard.

---

**Security Dashboard v1.0** - Advanced MVP for Privacy Monitoring