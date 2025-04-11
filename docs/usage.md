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

Refer to `simple_llm_call_example.py` for a straightforward example of making an LLM call with Prompt Sentinel.

## Example: Azure Client

The `azure_client_example.py` demonstrates how to use Prompt Sentinel with Azure client.

## Example: Local VLLM Detector

Use `local_vllm_detector_example.py` to see how a local VLLM detector is implemented.

## Example: Local HF Detector

The `local_hf_detector_example.py` provides an example of using a local Hugging Face detector.

## Example: Async Azure Calls

For asynchronous calls with Azure, refer to `azure_async_example.py`.

## Example: LiteLLM

The `litellm_example.py` shows how to use LiteLLM with Prompt Sentinel.