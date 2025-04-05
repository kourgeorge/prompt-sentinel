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
Prompt Sentinel is a Python library designed to help you protect sensitive data in your language model (LLM) interactions. It provides tools to detect, encode, and later decode sensitive information (e.g., API keys, passwords, tokens) in text before sending it to an LLM, ensuring that private or confidential information is not inadvertently exposed.

## Features

- **Sensitive Data Detection:**  
  Use detectors like `LLMSecretDetector` and `PythonStringDataDetector` to identify sensitive or private data in your text.
  
- **Tokenization & Replacement:**  
  Replace detected secrets with unique tokens (e.g., `__SECRET_1__`) so that the LLM operates on sanitized input. Later, you can decode the response to reinstate the original secrets.

- **Caching:**  
  Implement caching for repeated detections on the same text to reduce redundant API calls and improve performance.

- **Decorator Integration:**  
  Easily integrate secret sanitization into your LLM calling pipeline using the `prompt_sentinel` decorator. Preprocess your messages before they reach the LLM and post-process the responses to decode tokens.

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

## How It Works

1. **Pre-processing:**  
   The `prompt_sentinel` decorator intercepts your messages and calls `detect_and_encode_text` on each message's content. This function:
   - Uses a detector (e.g., `LLMSecretDetector`) to find sensitive information.
   - Caches detection results to avoid repeated API calls for the same text.
   - Replaces the sensitive parts with tokens (e.g., `__SECRET_1__`) and builds a mapping of tokens to secrets.

2. **LLM Call:**  
   The sanitized messages are sent to the LLM. The response is assumed to use tokens instead of the original sensitive values.

3. **Post-processing:**  
   After receiving the response, the decorator uses the token mapping to decode the tokens back to the original sensitive data.

## Customization

- **Detectors:**  
  You can implement your own secret detectors by extending the `SecretDetector` abstract base class. Check out the provided implementations in the `sentinel_detectors` module for guidance.

- **Caching:**  
  The detectors can use caching to avoid redundant API calls. In the provided implementation of `LLMSecretDetector`, caching is handled via an instance variable (`_detect_cache`).

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests on [GitHub](https://github.com/yourusername/prompt-sentinel). When contributing, please follow the guidelines in our [CONTRIBUTING.md](CONTRIBUTING.md).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
