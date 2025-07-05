#!/usr/bin/env python3
"""
Minimal Sentinel example - just the basics!
"""

import os
from sentinel.prompt_sentinel import sentinel
from sentinel.sentinel_detectors import RegexSecretDetector

# Configure telemetry
os.environ["PS_SERVER_URL"] = "http://localhost:8001"
os.environ["PS_APP_ID"] = "minimal_app"

# Protect your LLM calls with @sentinel decorator
@sentinel(detector=RegexSecretDetector())
def my_llm_function(prompt: str) -> str:
    # Your LLM call goes here (this is just a mock)
    return f"Mock LLM response to: {prompt}"

if __name__ == "__main__":
    # Test with a prompt containing sensitive data
    secret_prompt = "My API key is sk-1234567890abcdef, please help me debug this"
    
    print("Input:", secret_prompt)
    result = my_llm_function(secret_prompt)
    print("Output:", result)
    
    print("\n✅ Check the dashboard: http://localhost:8001/dashboard")
    print("🔐 Login: admin / admin123")