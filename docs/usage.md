# Usage Guide

Prompt Sentinel can be integrated into your LLM pipelines to protect sensitive data. Below are examples of how to use Prompt Sentinel in different scenarios.

## Decorating an LLM Function Call

You can use the `@sentinel` decorator to sanitize messages before they reach the LLM and decode responses after processing.

```python
@sentinel(detector=LLMSecretDetector(...))
def call_llm(messages):
    # Call the LLM with sanitized messages
    return response
```

## Wrapping an Entire Class

Wrap an entire class to automatically sanitize and decode messages for specified methods.

```python
InstrumentedClass = instrument_model_class(BaseChatModel, detector=LLMSecretDetector(...), methods_to_wrap=['invoke', 'ainvoke', 'stream', 'astream'])
llm = InstrumentedClass()
response = llm.invoke(messages)
```

## Example: Simple LLM Call

Refer to [`simple_llm_call_example.py`](examples/simple_llm_call_example.py) for a straightforward example of making an LLM call with Prompt Sentinel.

## Example: Azure Client

Refer to [`azure_client_example.py`](examples/azure_client_example.py) for usage with Azure.

## Example: Local VLLM Detector

Refer to [`local_vllm_detector_example.py`](examples/local_vllm_detector_example.py) for a local VLLM detector.

## Example: Local HF Detector

Refer to [`local_hf_detector_example.py`](examples/local_hf_detector_example.py) for a local Hugging Face detector.

## Example: Async Azure Calls

Refer to [`azure_async_example.py`](examples/azure_async_example.py) for asynchronous Azure calls.

## Example: LiteLLM

Refer to [`litellm_example.py`](examples/litellm_example.py) for LiteLLM usage.
`