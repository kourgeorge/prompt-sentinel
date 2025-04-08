from typing import List
import litellm
from dotenv import load_dotenv
from sentinel.sentinel_detectors import LLMSecretDetector, TrustableLLM
from sentinel.prompt_sentinel import sentinel

load_dotenv()  # Load .env credentials like LITELLM_API_KEY


# LiteLLM-compatible TrustableLLM wrapper
class LiteLLMTrustable(TrustableLLM):
    def __init__(self, model: str):
        self.model = model

    def predict(self, text: str, **kwargs) -> str:
        response = litellm.completion(
            model=self.model,
            messages=[{"role": "user", "content":text}],
            **kwargs
        )
        return response['choices'][0]['message']['content']


# Decorated function with secret redaction
@sentinel(detector=LLMSecretDetector(LiteLLMTrustable("gpt-4o-2024-08-06")))
def call_llm(messages: List[dict]) -> str:
    """
    Calls LiteLLM with messages. Secrets are sanitized by @sentinel.
    """
    try:
        response = litellm.completion(
            model="gpt-4o-2024-08-06",
            messages=messages,
            temperature=0.0,
            max_tokens=400,
            seed=123
        )
    except Exception as e:
        print(f"Error calling LLM: {e}.\nThe Messages: {messages}")
        return ""

    return response["choices"][0]["message"]["content"]


if __name__ == '__main__':
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user",
         "content": "Write a function in python logging in into my demo account with the following API function "
                    "demo_app_user_auth(username, password). "
                    "My email is kkk@gmail.com and password ABC123SECRETXYZ."},
    ]

    result = call_llm(messages)
    print("LLM Response:", result)
