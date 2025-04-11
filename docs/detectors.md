# Detectors

Prompt Sentinel provides various detectors to identify and sanitize sensitive data during interactions with language models. Below are examples and explanations for each type of detector, with a focus on local LLM-based detectors.

## Local VLLM Detector

The Local VLLM Detector uses a local language model to detect sensitive information. Here's a working example:

### Example: Local VLLM Detector

```python
import asyncio
from typing import Optional

import openai
from dotenv import load_dotenv
from sentinel import instrument_model_class, LLMSecretDetector, TrustableLLM
import os

load_dotenv()  # take environment variables

class LocalVllmDetector(TrustableLLM):
    def __init__(
            self,
            model_name: str = "Qwen/Qwen2.5-1.5B-Instruct",
            base_url: str = "http://localhost:8080/v1",
            api_key: Optional[str] = "dummy",  # vLLM ignores this, but OpenAI client requires it
    ):
        self.model_name = model_name
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url)

    def predict(self, text: str, **kwargs) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": text}],
            temperature=0,
            max_tokens=512,
            **kwargs
        )
        return response.choices[0].message.content.strip()

class FakeResponse:
    def __init__(self, content):
        self.role = 'AI'
        self.content = content

class FakeChatModel:

    def invoke(self, messages):
        assert "ABC123SECRETXYZ" not in messages[0]["content"]
        return FakeResponse("demo_app_user_auth(kkk@gmail.com, ABC123SECRETXYZ).")

    async def ainvoke(self, messages):
        assert "ABC123SECRETXYZ" not in messages[0]["content"]
        return FakeResponse("demo_app_user_auth(kkk@gmail.com, ABC123SECRETXYZ).")

    def untouched_method(self):
        return "leave me alone"

async def main():
    messages = [
        {"role": "user", "content": "Write a function in python logging in into an my demo account with the following "
                                        "API function demo_app_user_auth(username, passowrd). "
                                        "My email is kkk@gmail.com and password ABC123SECRETXYZ."},
    ]

    llm = FakeChatModel()
    detector = LLMSecretDetector(LocalVllmDetector(model_name='Qwen/Qwen2.5-1.5B-Instruct'))
    wrapped_llm = instrument_model_class(llm, detector)
    result = await wrapped_llm.ainvoke(messages)

    print("Wrapped LLM Response:", result.content)
    assert 'ABC123SECRETXYZ' in result.content

# --- Run the test ---
if __name__ == '__main__':
    asyncio.run(main())
```

### Explanation

- **Initialization**: The `LocalVllmDetector` is initialized with a model name and base URL, setting up a client to interact with the local LLM.
- **Detection**: The `LLMSecretDetector` is used to detect and sanitize sensitive information in the input messages.
- **Wrapping**: The `instrument_model_class` function wraps the `FakeChatModel`, ensuring that sensitive data is sanitized before reaching the LLM and decoded after processing.
- **Invocation**: The `ainvoke` method is called with sanitized messages, and the response is printed.

## Other Detectors

### Python String Data Detector

The `PythonStringDataDetector` can be used to identify sensitive data in Python strings. Here's how you can use it:

```python
from sentinel import PythonStringDataDetector

detector = PythonStringDataDetector()
# Use the detector in your LLM pipeline
```

### Custom Detectors

You can implement your own secret detectors by extending the `SecretDetector` abstract base class. Check out the provided implementations in the `sentinel_detectors` module for guidance.