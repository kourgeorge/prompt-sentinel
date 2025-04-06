
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

- **Automatic Secret Decoding in Tools:**  
  Tool input and output are automatically decoded before and after execution, ensuring that tools receive original secrets (e.g., passwords, API keys) even when the LLM was only shown sanitized tokens.

- **Decorator Integration:**  
  Easily integrate secret sanitization into your LLM calling pipeline using the `@sentinel` decorator. Preprocess your messages before they reach the LLM and post-process the responses to decode tokens.

- **Tool Wrapping:**  
  Automatically wraps LangChain-compatible tools by intercepting the `_run()` method, decoding secrets before tool logic is invoked.

- **Caching:**  
  Implement caching for repeated detections on the same text to reduce redundant API calls and improve performance.

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

8. **Check: Does the LLM Response Contain a Tool Call?**  
   - If **yes**:  
     a. Intercept the tool's `_run()` method  
     b. Decode any secrets in the tool input using the same mapping  
     c. Execute the tool with the original values
   - If **no**:  
     Return the decoded LLM response directly to the user.

## Customization

- **Detectors:**  
  You can implement your own secret detectors by extending the `SecretDetector` abstract base class. Check out the provided implementations in the `sentinel_detectors` module for guidance.

- **Context Management:**  
  Internally, a singleton context is used to persist secret mappings during LLM interaction and tool invocation. This ensures secrets encoded in the LLM prompt are automatically decoded before tool execution.

- **Tool Wrapping:**  
  To support sensitive data in tools, use `wrap_tool_with_decoder()` to transparently decode tool input before execution.

- **Caching:**  
  The detectors can use caching to avoid redundant API calls. In the provided implementation of `LLMSecretDetector`, caching is handled via an instance variable (`_detect_cache`).

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests on [GitHub](https://github.com/yourusername/prompt-sentinel). When contributing, please follow the guidelines in our [CONTRIBUTING.md](CONTRIBUTING.md).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
