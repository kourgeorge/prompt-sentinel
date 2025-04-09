from sentinel.prompt_sentinel import sentinel
from sentinel.sentinel_detectors import SecretDetector


def instrument_model_class(model_class, detector: SecretDetector, methods_to_wrap=None):
    """
       Patches the given LLM model class by wrapping selected methods with the Sentinel decorator,
       enabling automatic detection and sanitization of sensitive data during LLM interactions.

       This function creates a deep copy of the provided model class and decorates its key
       LLM interaction methods (e.g., 'invoke', 'ainvoke', 'stream', 'astream') using the
       specified `SecretDetector`. This allows the model to sanitize inputs and restore original
       values transparently, without altering the logic of the core model.

       Parameters:
       ----------
       model_class : class
           The LLM model class to be patched. A deep copy of this class will be modified
           and returned with wrapped methods.

       detector : SecretDetector
           An instance of `SecretDetector` used to identify and mask sensitive information
           in the model input.

       methods_to_wrap : list of str, optional
           A list of method names to wrap with the Sentinel decorator. If not provided,
           defaults to ['invoke', 'ainvoke', 'stream', 'astream'].

       Returns:
       -------
       patched_class : class
           A modified version of the input model class with selected methods wrapped
           for secure, sanitized communication.

       Example:
       -------
       ```python
       from prompt_sentinel import patch_model_class_with_sentinel, SecretDetector

       MyModel = patch_model_class_with_sentinel(MyModel, detector=SecretDetector())
       model = MyModel(...)
       response = model.invoke("API key: sk-123...")  # Sanitized automatically
       ```
       """

    if methods_to_wrap is None:
        methods_to_wrap = ['invoke', 'ainvoke', 'stream', 'astream']

    # Create a new subclass with a distinct name
    class_name = f"SentinelPatched{model_class.__name__}"
    new_model_class = type(class_name, (model_class,), {})

    # Wrap specified methods with the sentinel decorator
    for method_name in methods_to_wrap:
        if hasattr(model_class, method_name):
            original_method = getattr(model_class, method_name)
            if callable(original_method):
                decorated_method = sentinel(detector)(original_method)
                setattr(new_model_class, method_name, decorated_method)

    # Assign a unique ID to the new class
    new_model_class.__name__ = class_name
    new_model_class.__qualname__ = class_name

    return new_model_class
