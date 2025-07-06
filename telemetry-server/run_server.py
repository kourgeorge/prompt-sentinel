#!/usr/bin/env python3
"""
Simple script to run the Sentinel Telemetry Server
"""

import os
import sys
import uvicorn

def main():
    """Main function to start the telemetry server"""
    print("🛡️  Sentinel Telemetry Server")
    print("=" * 50)
    
    # Configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8001))  # Updated to match new default port
    
    print(f"Starting server on {host}:{port}")
    print(f"Dashboard URL: http://localhost:{port}")
    print(f"API Endpoint: http://localhost:{port}/api/report")
    print("\nDemo Login Credentials:")
    print("- Admin: admin / admin123")
    print("- Officer: officer1 / secure123")
    print("=" * 50)
    
    try:
        # Start the server
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()