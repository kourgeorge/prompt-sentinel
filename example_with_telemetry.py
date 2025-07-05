#!/usr/bin/env python3
"""
Example script demonstrating Sentinel with telemetry reporting.
This script shows how to use Sentinel with the telemetry dashboard.
"""

import os
import time
from sentinel.prompt_sentinel import sentinel
from sentinel.sentinel_detectors import RegexSecretDetector, LLMSecretDetector
from sentinel.session_context import SessionContext

# Configure telemetry server
os.environ["PS_SERVER_URL"] = "http://localhost:8000"
os.environ["PS_APP_ID"] = "example_app"

# Create a simple LLM mock for demonstration
class MockLLM:
    def predict(self, text: str) -> str:
        # Simple mock that returns the prompt as-is
        return f"LLM Response: {text}"

# Example prompts with various types of sensitive data
example_prompts = [
    "Please help me with my API key: sk-1234567890abcdef",
    "My password is MySecretPass123! for the database",
    "Here's my credit card: 4532 1234 5678 9012",
    "Contact info: john.doe@company.com, phone: 555-123-4567",
    "Database connection: postgresql://user:secret@localhost/db",
    "My SSN is 123-45-6789 for verification",
    "JWT token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "This is a normal prompt without secrets"
]

def run_example_with_regex_detector():
    """Example using regex-based secret detection"""
    print("🔍 Running example with Regex Secret Detector")
    print("=" * 60)
    
    # Create detector
    detector = RegexSecretDetector()
    
    # Create a mock LLM function
    @sentinel(detector=detector)
    def call_llm(prompt: str) -> str:
        # Simulate LLM call
        time.sleep(0.1)  # Simulate processing time
        return f"LLM processed: {prompt}"
    
    # Process each example prompt
    for i, prompt in enumerate(example_prompts[:4], 1):
        print(f"\n--- Example {i} ---")
        print(f"Original prompt: {prompt}")
        
        try:
            response = call_llm(prompt)
            print(f"LLM response: {response}")
        except Exception as e:
            print(f"Error: {e}")
        
        print("-" * 40)

def run_example_with_llm_detector():
    """Example using LLM-based secret detection"""
    print("\n🤖 Running example with LLM Secret Detector")
    print("=" * 60)
    
    # Create mock trustable LLM
    trustable_llm = MockLLM()
    
    # Create detector
    detector = LLMSecretDetector(trustable_llm)
    
    # Create a mock LLM function
    @sentinel(detector=detector)
    def call_llm_with_ai_detector(prompt: str) -> str:
        # Simulate LLM call
        time.sleep(0.1)  # Simulate processing time
        return f"AI-LLM processed: {prompt}"
    
    # Process remaining example prompts
    for i, prompt in enumerate(example_prompts[4:], 5):
        print(f"\n--- Example {i} ---")
        print(f"Original prompt: {prompt}")
        
        try:
            response = call_llm_with_ai_detector(prompt)
            print(f"LLM response: {response}")
        except Exception as e:
            print(f"Error: {e}")
        
        print("-" * 40)

def demonstrate_session_context():
    """Demonstrate session context features"""
    print("\n📊 Demonstrating Session Context")
    print("=" * 60)
    
    # Create custom session context
    session_context = SessionContext(
        app_id="custom_app_demo",
        server_url="http://localhost:8000"
    )
    
    detector = RegexSecretDetector()
    
    @sentinel(detector=detector, session_context=session_context)
    def process_sensitive_data(data: str) -> str:
        return f"Processed: {data}"
    
    # Process a prompt with session context
    sensitive_prompt = "Please process this API key: sk-abcdef123456 and password: admin123"
    print(f"Processing with custom session: {sensitive_prompt}")
    
    result = process_sensitive_data(sensitive_prompt)
    print(f"Result: {result}")
    
    # Show session info
    print(f"\nSession Info:")
    print(f"App ID: {session_context.app_id}")
    print(f"Session ID: {session_context.session_id}")
    print(f"Server URL: {session_context.server_url}")
    print(f"Secrets in vault: {len(session_context.get_secret_mapping())}")

def main():
    """Main function to run all examples"""
    print("🛡️  Sentinel with Telemetry Dashboard - Example Script")
    print("=" * 70)
    
    # Check if telemetry server is configured
    server_url = os.getenv("PS_SERVER_URL", "Not configured")
    app_id = os.getenv("PS_APP_ID", "Not configured")
    
    print(f"Telemetry Server URL: {server_url}")
    print(f"App ID: {app_id}")
    
    if server_url == "Not configured":
        print("\n⚠️  Warning: Telemetry server not configured!")
        print("Start the telemetry server first: cd telemetry-server && python main.py")
    
    print("\n" + "=" * 70)
    
    try:
        # Run examples
        run_example_with_regex_detector()
        run_example_with_llm_detector()
        demonstrate_session_context()
        
        print("\n✅ All examples completed successfully!")
        print("\n📊 Check the telemetry dashboard at: http://localhost:8000")
        print("Login with: admin / admin123")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        print("Make sure the telemetry server is running.")

if __name__ == "__main__":
    main()