
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

You can wrap all tools used by your agent like this:

```python
self.tools = [wrap_tool_with_decoder(tool) for tool in self.tools]
```

This ensures tools receive decoded (original) values like passwords, API keys, or tokens.

## How It Works

```mermaid
flowchart TD
    A[User Input] --> B[Sanitize Input via @sentinel]
    B --> C[Detect Secrets with SecretDetector]
    C --> D[Replace Secrets with Tokens (__SECRET_1__)]
    D --> E[Send Sanitized Input to LLM]
    E --> F[LLM Generates Response with Tokens]
    F --> G[Decode LLM Output using Secret Mapping]
    G --> H{LLM Response Contains Tool Call?}
    H -- Yes --> I[Intercept Tool _run()]
    I --> J[Decode Tool Input with Secret Mapping]
    J --> K[Tool Executes with Original Secrets]
    H -- No --> L[Return Final Response to User]
    K --> L
```

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
