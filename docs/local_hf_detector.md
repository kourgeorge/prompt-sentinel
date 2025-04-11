# Local Hugging Face Detector

The Local Hugging Face Detector leverages the Hugging Face `transformers` library to detect and sanitize sensitive data using a local language model. Below is a detailed example and explanation of how to implement and use this detector.

## Example: Local Hugging Face Detector

This example demonstrates how to use a local Hugging Face model to detect secrets in text input.

### Code Example

```python
import asyncio
from dotenv import load_dotenv
from sentinel import instrument_model_class, LLMSecretDetector, TrustableLLM
import os

# Load environment variables from a .env file
load_dotenv()

try:
    from transformers import pipeline

    # Define a class that extends TrustableLLM to use a Hugging Face model
    class LocalHFLLM(TrustableLLM):
        def __init__(self, model_name: str = 'Qwen/Qwen2.5-1.5B-Instruct', token=os.getenv('HUGGING_FACE_HUB_TOKEN')):
            # Initialize a text generation pipeline with the specified model and token
            self.generator = pipeline("text-generation", model=model_name, device=0, token=token)

        def predict(self, text: str,  **kwargs) -> str:
            # Generate text using the model, with specific parameters
            outputs = self.generator(text, max_new_tokens=512, do_sample=False, temperature=0)
            full_output = outputs[0]['generated_text']
            # Remove the input prompt from the beginning of the generated text
            generated_part = full_output[len(text):].strip()
            return generated_part

except ImportError:
    HuggingFaceLLM = None

# Define a fake response class to simulate LLM responses
class FakeResponse:
    def __init__(self, content):
        self.role = 'AI'
        self.content = content

# Define a fake chat model class to simulate LLM interactions
class FakeChatModel:

    def invoke(self, messages):
        # Ensure sensitive information is not present in the input messages
        assert "ABC123SECRETXYZ" not in messages[0]["content"]
        return FakeResponse("demo_app_user_auth(kkk@gmail.com, ABC123SECRETXYZ).")

    async def ainvoke(self, messages):
        # Ensure sensitive information is not present in the input messages
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

    # Define a custom prompt to guide the model in extracting secrets
    custom_prompt = (
        "Extract secrets from the following:\n\n"
        "Only include API keys, secrets, tokens, or credentials. Use the following output format as JSON: {{\"secrets\": [...]}}\n\n"
        "Text: {text}"
    )

    # Initialize the detector with the local Hugging Face model and custom prompt
    detector = LLMSecretDetector(LocalHFLLM(model_name='Qwen/Qwen2.5-1.5B-Instruct'), prompt_format=custom_prompt)
    # Wrap the fake chat model with the detector
    wrapped_llm = instrument_model_class(FakeChatModel, detector)()
    # Invoke the wrapped model asynchronously with sanitized messages
    result = await wrapped_llm.ainvoke(messages)

    # Print the response from the wrapped LLM
    print("Wrapped LLM Response:", result.content)
    # Assert that the original secret is present in the response
    assert 'ABC123SECRETXYZ' in result.content

# --- Run the test ---
if __name__ == '__main__':
    asyncio.run(main())
```

### Explanation

- **Initialization**: The `LocalHFLLM` class initializes a text generation pipeline using a specified model name and token. This setup allows the model to generate text based on input prompts.

- **Custom Prompt**: A custom prompt format is defined to instruct the model to extract secrets from the input text. This approach provides flexibility in targeting specific types of sensitive information.

- **Detection**: The `LLMSecretDetector` is used with the custom prompt to detect and sanitize sensitive information in the input messages. This ensures that sensitive data is not exposed during LLM interactions.

- **Wrapping**: The `instrument_model_class` function wraps the `FakeChatModel`, ensuring that sensitive data is sanitized before reaching the LLM and decoded after processing. This integration makes the detection and sanitization process seamless and efficient.

- **Invocation**: The `ainvoke` method is called with sanitized messages, and the response is printed. This demonstrates the effectiveness of the detector in identifying and handling sensitive data.

## Customization

The Local Hugging Face Detector can be customized by modifying the model name, token, and prompt format. This allows users to tailor the detection process to their specific needs and use cases.