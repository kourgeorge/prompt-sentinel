from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool

from sentinel.prompt_sentinel import sentinel
from sentinel.sentinel_detectors import SecretDetector

from functools import wraps
from sentinel.secret_context import get_secret_mapping
from sentinel.prompt_sentinel import decode_text


def wrap_chat_model_with_sentinel(model: BaseChatModel, detector: SecretDetector):
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

