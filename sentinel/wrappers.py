from langchain_core.language_models import BaseChatModel

from sentinel.prompt_sentinel import sentinel
from sentinel.sentinel_detectors import SecretDetector


def wrap_basechatmodel_with_sentinel(model: BaseChatModel, detector: SecretDetector):
    """
    Wraps the key LLM call methods of the given model instance with the sentinel decorator.
    This patches the model's class so that the methods are overridden.
    """
    methods_to_wrap = ['invoke', 'ainvoke', 'stream', 'astream']

    for method_name in methods_to_wrap:
        if hasattr(model, method_name):
            original_method = getattr(model, method_name)
            if callable(original_method):
                decorated_method = sentinel(detector)(original_method)
                setattr(type(model), method_name, decorated_method)
    return model
