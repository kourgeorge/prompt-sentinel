#!/usr/bin/env python3
"""
Simple example using Prompt Sentinel with telemetry reporting.
This script demonstrates how to use the @sentinel decorator to protect
sensitive data in LLM prompts while sending telemetry to the dashboard.
"""

import os
import time
from sentinel.prompt_sentinel import sentinel
from sentinel.sentinel_detectors import RegexSecretDetector
from sentinel.session_context import SessionContext

# Configure telemetry to send data to our dashboard
os.environ["PS_SERVER_URL"] = "http://localhost:8001"
os.environ["PS_APP_ID"] = "simple_example_app"

print("🛡️  Simple Sentinel Example with Telemetry")
print("=" * 50)
print(f"Telemetry Server: {os.environ['PS_SERVER_URL']}")
print(f"App ID: {os.environ['PS_APP_ID']}")
print("=" * 50)

# Create a simple mock LLM function
def mock_llm_call(prompt: str) -> str:
    """
    Mock LLM function that simulates calling an AI model.
    In a real application, this would call OpenAI, Anthropic, etc.
    """
    # Simulate processing time
    time.sleep(0.5)
    
    # Return a mock response
    return f"LLM Response: I've processed your request about: {prompt[:50]}..."

# Create a Sentinel-protected LLM function using regex detector
@sentinel(detector=RegexSecretDetector())
def safe_llm_call(prompt: str) -> str:
    """
    LLM function protected by Sentinel.
    Sensitive data will be detected, masked, and reported to telemetry.
    """
    return mock_llm_call(prompt)

# Test prompts with various types of sensitive data
test_prompts = [
    {
        "name": "API Key Example",
        "prompt": "Please help me debug this API call. My key is sk-1234567890abcdef"
    },
    {
        "name": "Password Example", 
        "prompt": "I can't login to the database. My password is MySecretPass123!"
    },
    {
        "name": "Credit Card Example",
        "prompt": "Process this payment with card number 4532 1234 5678 9012"
    },
    {
        "name": "Email & Phone Example",
        "prompt": "Contact customer john.doe@company.com or call 555-123-4567"
    },
    {
        "name": "Safe Example",
        "prompt": "What's the weather like today? This prompt has no secrets."
    }
]

def run_example():
    """Run the Sentinel example with telemetry reporting"""
    
    print("\n🚀 Running Sentinel examples...")
    print("📊 Check the dashboard at: http://localhost:8001/dashboard")
    print("🔐 Login with: admin / admin123")
    print("\n")
    
    for i, test in enumerate(test_prompts, 1):
        print(f"📝 Example {i}: {test['name']}")
        print(f"   Input: {test['prompt']}")
        
        try:
            # Call the Sentinel-protected function
            response = safe_llm_call(test['prompt'])
            print(f"   Output: {response}")
            
            # Add a small delay between calls
            time.sleep(1)
            
        except Exception as e:
            print(f"   Error: {e}")
        
        print("-" * 60)
    
    print("\n✅ All examples completed!")
    print("\n📊 Telemetry Data Sent!")
    print("   - Check your dashboard to see the privacy events")
    print("   - Look for the 'simple_example_app' in the applications list")
    print("   - Review detected secrets and risk levels")

def demonstrate_custom_session():
    """Demonstrate using a custom session context"""
    
    print("\n🔧 Custom Session Example")
    print("-" * 30)
    
    # Create a custom session context
    custom_session = SessionContext(
        app_id="custom_session_demo",
        server_url="http://localhost:8001"
    )
    
    # Create a function with custom session
    @sentinel(detector=RegexSecretDetector(), session_context=custom_session)
    def custom_llm_call(prompt: str) -> str:
        return mock_llm_call(prompt)
    
    # Test with sensitive data
    sensitive_prompt = "Connect to database with postgresql://admin:secret123@localhost/mydb"
    print(f"Input: {sensitive_prompt}")
    
    response = custom_llm_call(sensitive_prompt)
    print(f"Output: {response}")
    
    print(f"Session ID: {custom_session.session_id}")
    print(f"Secrets in vault: {len(custom_session.get_secret_mapping())}")

if __name__ == "__main__":
    try:
        # Run the main examples
        run_example()
        
        # Demonstrate custom session
        demonstrate_custom_session()
        
        print("\n" + "=" * 50)
        print("🎉 Demo completed successfully!")
        print("📈 View telemetry data at: http://localhost:8001/dashboard")
        print("=" * 50)
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Error running demo: {e}")
        print("Make sure the telemetry server is running on port 8001")