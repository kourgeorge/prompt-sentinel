# API Reference

## Installation

To install Prompt Sentinel, use the following command:

```bash
pip install prompt-sentinel
```

For more details, refer to the [Installation Instructions](installation.md).

---

## Table of Contents
- [@sentinel](#sentinel)
- [instrument_model_class](#instrument_model_class)
- [LLMSecretDetector](#llmsecretdetector)
- [PythonStringDataDetector](#pythonstringdatadetector)
- [Customization](#customization)
- [Caching](#caching)

---

## Introduction

Prompt Sentinel is a Python library designed to protect sensitive data during interactions with language models (LLMs). It detects and sanitizes confidential information—such as passwords, tokens, and secrets—before sending input to the LLM and restores the original values seamlessly after processing. This ensures secure and transparent interactions with LLMs.

---

## `@sentinel`

The `@sentinel` decorator automatically sanitizes input messages before they reach the LLM and decodes responses after processing.

**Parameters:**
- `detector`: An instance of a secret detector, such as `LLMSecretDetector`.

**Example:**

```python
from sentinel import sentinel, LLMSecretDetector
messages = [
    {"role": "user", "content": "My API key is hf-mfehcnsjk8"}
@sentinel(detector=LLMSecretDetector(...))
def call_llm(messages):
    return response
 ```

### `instrument_model_class`

This function wraps an entire class to automatically sanitize and decode messages for specified methods.

**Parameters:**
- `base_class`: The base class to be instrumented.
- `detector`: An instance of a secret detector.
- `methods_to_wrap`: A list of method names to be wrapped for sanitization.

**Example:**
```python
from sentinel import instrument_model_class, LLMSecretDetector

InstrumentedClass = instrument_model_class(BaseChatModel, detector=LLMSecretDetector(...), methods_to_wrap=['invoke', 'ainvoke'])
messages = [
    {"role": "user", "content": "My API key is hf-mfehcnsjk8"}
llm = InstrumentedClass()
response = llm.invoke(messages)
 ```

### `LLMSecretDetector`

A detector class used to identify sensitive or private data in text. It can be customized to use different detection mechanisms. 

**Features:**

- Supports custom prompts for targeted detection.
- Can integrate with local or external LLMs.
**Example:**
```python
from sentinel import LLMSecretDetector

custom_prompt = (
    "Extract secrets from the following:\n\n"
    "Only include API keys, secrets, tokens, or credentials. Use the following output format as JSON: {{\"secrets\": [...]}}\n\n"
    "Text: {text}"
)

detector = LLMSecretDetector(model, prompt_format=custom_prompt)
```

### `PythonStringDataDetector`

Another detector class that can be used to identify sensitive data in Python strings.

## Customization

You can implement your own secret detectors by extending the `SecretDetector` abstract base class. Check out the provided implementations in the `sentinel_detectors` module for guidance.

## Caching

The detectors can use caching to avoid redundant API calls. In the provided implementation of `LLMSecretDetector`, caching is handled via an instance variable (`_detect_cache`).