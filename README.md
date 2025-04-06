
# Prompt Sentinel

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [How It Works](#how-it-works)
- [Customization](#customization)
- [Contributing](#contributing)
- [License](#license)

## Introduction
Prompt Sentinel is a Python library that helps safeguard sensitive data during interactions with language models (LLMs). 
It automatically sanitizes information like passwords, tokens, and secrets before sending input to the LLM, minimizing the risk of unintentional exposure. 
Once the response is received, the original masked values are restored.
## Features

- **Sensitive Data Detection:**  
  Use detectors like `LLMSecretDetector` and `PythonStringDataDetector` to identify sensitive or private data in your text.

- **Automatic Sanitization through secret masking:**  
  Mechanisms for replacing detected secrets with unique mask tokens (e.g., `__SECRET_1__`) so that the LLM operates on sanitized input. 
- Following the LLM returned output, the response is decoded to reinstate the original secrets.

- **Decorator Integration:**  
  Easily integrate secret sanitization into your LLM calling pipeline using the `@sentinel` decorator. Preprocess your messages before they reach the LLM and post-process the responses to decode tokens.

- **Caching:**  
  Implement caching for repeated detections on the same text to reduce redundant API calls and improve performance.

- **Async LLM calls**
  Support async function/method LLM call decoration.

## Installation

Install the package using pip (or include it in your project as needed):

```bash
pip install prompt-sentinel
```

*Note: This package requires Python 3.7 or higher.*

## Usage

Below are examples of how to use Prompt Sentinel in different LLM pipelines. For detailed examples, please refer to the `examples` directory in the repository.

### Decorating an LLM Function Call

```python
@sentinel(detector=LLMSecretDetector(...))
def call_llm(messages):
    # Call the LLM with sanitized messages
    return response
```

### Wrapping an Entire BaseChatModel

```python
llm = BaseChatModel(...)
wrapped_llm = wrap_chat_model_with_sentinel(llm, detector=LLMSecretDetector(...))
response = wrapped_llm.invoke(messages)
```

### Wrapping LangChain Tools to Automatically Decode Input

```python
from prompt_sentinel.wrappers import wrap_tool_with_decoder

wrapped_tool = wrap_tool_with_decoder(tool)
```

This ensures tools receive decoded (original) values like passwords, API keys, or tokens.

## How It Works

Step-by-step flow:

1. **User Input**  
   The user submits a prompt containing potential secrets.

2. **Sanitize Input via `@sentinel`**  
   The decorator intercepts the prompt before it reaches the LLM.

3. **Detect Secrets with SecretDetector**  
   A detector scans the prompt for sensitive information like passwords, keys, or tokens.

4. **Replace Secrets with Tokens (e.g., `__SECRET_1__`)**  
   Each secret is replaced by a unique placeholder token and stored in a mapping.

5. **Send Sanitized Input to LLM**  
   The modified, tokenized prompt is passed to the language model.

6. **LLM Generates Response with Tokens**  
   The response from the model may include those placeholder tokens.

7. **Decode LLM Output using Secret Mapping**  
   Tokens are replaced with their original secrets using the stored mapping.

## Customization

- **Detectors:**  
  You can implement your own secret detectors by extending the `SecretDetector` abstract base class. Check out the provided implementations in the `sentinel_detectors` module for guidance.

- **Context Management:**  
  Internally, a singleton context is used to persist secret mappings during LLM interaction and tool invocation. This ensures secrets encoded in the LLM prompt are automatically decoded before tool execution.

- **Caching:**  
  The detectors can use caching to avoid redundant API calls. In the provided implementation of `LLMSecretDetector`, caching is handled via an instance variable (`_detect_cache`).

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests on [GitHub](https://github.com/yourusername/prompt-sentinel). When contributing, please follow the guidelines in our [CONTRIBUTING.md](CONTRIBUTING.md).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
