# Sentinel Parameter Options

The `@sentinel` decorator and related functions in Prompt Sentinel offer various configuration options to customize the detection and sanitization process. Below are the key options and examples of how to use them.

## Detector

The `detector` parameter specifies the detector to use for identifying sensitive data. This is the primary parameter for the `@sentinel` decorator.

### Example: Using LLMSecretDetector

```python
from sentinel import sentinel, LLMSecretDetector

@sentinel(detector=LLMSecretDetector(...))
def call_llm(messages):
    # Call the LLM with sanitized messages
    return response
```

## Methods to Wrap

When using `instrument_model_class`, you can specify which methods of the class should be wrapped for sanitization using the `methods_to_wrap` parameter.

### Example: Wrapping Specific Methods

```python
from sentinel import instrument_model_class, LLMSecretDetector

InstrumentedClass = instrument_model_class(BaseChatModel, detector=LLMSecretDetector(...), methods_to_wrap=['invoke', 'ainvoke'])
llm = InstrumentedClass()
response = llm.invoke(messages)
```

## Custom Detectors

You can implement your own secret detectors by extending the `SecretDetector` abstract base class. This allows for tailored detection mechanisms to suit specific needs.

### Example: Custom Detector

```python
from sentinel import SecretDetector

class CustomDetector(SecretDetector):
    def detect(self, text):
        # Custom detection logic
        return detected_secrets

custom_detector = CustomDetector()
# Use the custom detector in your LLM pipeline
```

## Additional Options

While the primary focus is on detectors and method wrapping, additional options may be available depending on the specific implementation and use case. Refer to the source code and examples for further customization possibilities.