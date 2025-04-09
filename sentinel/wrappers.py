from sentinel.prompt_sentinel import sentinel
from sentinel.sentinel_detectors import SecretDetector

try:
    from langchain_core.language_models import BaseChatModel
    from langchain_core.tools import BaseTool


    def create_chat_model_proxy_class(base_cls, methods_to_wrap=None):
        """
        Dynamically creates a proxy class that wraps methods of a base chat model class
        with a `sentinel` decorator for secret detection and sanitization.

        This is useful when you want to intercept and sanitize inputs to selected methods
        (e.g., `invoke`, `ainvoke`, etc.) of a language model wrapper such as `AzureChatOpenAI`
        or other LangChain-compatible classes.

        Args:
            base_cls (type): The base class of the chat model (e.g., `AzureChatOpenAI`, `BaseChatModel`).
            methods_to_wrap: The method to wrap

        Returns:
            ChatModelProxy (type): A subclass of `base_cls` that intercepts and wraps selected methods
            on an instance using the sentinel secret detector.

        The returned proxy class:
            - Delegates all other attribute accesses to the original model instance.
            - Wraps specified methods (default: ['invoke', 'ainvoke', 'stream', 'astream']) with the sentinel.
            - Supports both sync and async methods.
            - Allows calls via `type(proxy_instance).invoke(...)` due to dynamic method overrides.

        Example usage:
            ProxyClass = create_chat_model_proxy_class(AzureChatOpenAI)
            proxy = ProxyClass(model=original_model, detector=detector)

        Internal Structure:
            - `_model`: The original model being wrapped.
            - `_detector`: The LLMSecretDetector instance.
            - `_methods_to_wrap`: List of method names to wrap.
            - `_wrapped_methods`: A dict of {method_name: wrapped_method}

        Limitations:
            - Uses `object.__setattr__` to bypass Pydantic restrictions.
            - Wrapped methods are explicitly assigned to the proxy instance.
        """

        class ChatModelProxy(base_cls):
            def __init__(self, model, detector):
                object.__setattr__(self, "_model", model)
                object.__setattr__(self, "_detector", detector)
                object.__setattr__(self, "_methods_to_wrap", methods_to_wrap or ['invoke', 'ainvoke', 'stream', 'astream'])
                object.__setattr__(self, "_wrapped_methods", {})

                for method_name in object.__getattribute__(self, "_methods_to_wrap"):
                    if hasattr(model, method_name):
                        method = getattr(model, method_name)
                        if callable(method):
                            wrapped = sentinel(detector)(method)
                            object.__getattribute__(self, "_wrapped_methods")[method_name] = wrapped

                            # Bind the wrapped method to self so it overrides class-level dispatch
                            bound = wrapped.__get__(self, type(self))
                            object.__setattr__(self, method_name, bound)

            def __getattr__(self, name):
                wrapped_methods = object.__getattribute__(self, "_wrapped_methods")
                if name in wrapped_methods:
                    return wrapped_methods[name].__get__(self, type(self))
                model = object.__getattribute__(self, "_model")
                return getattr(model, name)

            def __dir__(self):
                base = set(dir(object.__getattribute__(self, "_model")))
                local = set(self.__dict__.keys())
                extra = set(object.__getattribute__(self, "_wrapped_methods").keys())
                return list(base | local | extra)

        # Add method overrides to support direct calls like type(llm).invoke(...)
        for method_name in methods_to_wrap:
            def make_override(name):
                def override(self, *args, **kwargs):
                    method = object.__getattribute__(self, "_wrapped_methods").get(name)
                    if method is None:
                        raise AttributeError(f"Wrapped method '{name}' not found.")
                    return method(*args, **kwargs)
                return override

            setattr(ChatModelProxy, method_name, make_override(method_name))

        def __deepcopy__(self, memo):
            return self

        return ChatModelProxy


    def wrap_chat_model_with_sentinel(model: BaseChatModel, detector: SecretDetector,
                                      methods_to_wrap=None):
        """
           Wraps the given chat model instance with a sentinel-powered proxy class that
           sanitizes input to specified methods.

           Args:
               model (BaseChatModel): The LLM model instance to wrap.
               detector (SecretDetector): The secret detection/sanitization logic.
               methods_to_wrap (list[str]): Method names to wrap (default: common LLM methods).

           Returns:
               An instance of a proxy class that behaves like `model`, but with secret-aware methods.
           """
        if methods_to_wrap is None:
            methods_to_wrap = ['invoke', 'ainvoke', 'stream', 'astream']
        ProxyClass = create_chat_model_proxy_class(type(model), methods_to_wrap)
        return ProxyClass(model=model, detector=detector)


except ImportError:
    pass


def wrap_chat_model_class_with_sentinel(model_instance, detector: SecretDetector,
                                        methods_to_wrap=None):
    """
    Wraps the key LLM call methods of the given model instance with the sentinel decorator.
    This patches the model's class so that the methods are overridden.
    """

    if methods_to_wrap is None:
        methods_to_wrap = ['invoke', 'ainvoke', 'stream', 'astream']
    for method_name in methods_to_wrap:
        if hasattr(model_instance, method_name):
            original_method = getattr(model_instance, method_name)
            if callable(original_method):
                decorated_method = sentinel(detector)(original_method)
                setattr(type(model_instance), method_name, decorated_method)
    return model_instance
