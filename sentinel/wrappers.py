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


def decode_dict(d: dict, mapping: dict) -> dict:
    return {
        k: decode_text(v, mapping) if isinstance(v, str) else v
        for k, v in d.items()
    }

def wrap_tool_with_decoder(tool):
    # Handle LangChain tools with custom `_run()` methods
    if isinstance(tool, BaseTool) and hasattr(tool, "_run"):
        original_run = tool._run

        @wraps(original_run)
        def wrapped_run(*args, **kwargs):
            mapping = get_secret_mapping()

            # Decode string or dict inputs
            decoded_args = list(args)
            for i, arg in enumerate(decoded_args):
                if isinstance(arg, str):
                    decoded_args[i] = decode_text(arg, mapping)
                elif isinstance(arg, dict):
                    decoded_args[i] = decode_dict(arg, mapping)

            for k, v in kwargs.items():
                if isinstance(v, str):
                    kwargs[k] = decode_text(v, mapping)
                elif isinstance(v, dict):
                    kwargs[k] = decode_dict(v, mapping)

            return original_run(*decoded_args, **kwargs)

        tool._run = wrapped_run
        return tool

    return tool  # Unmodified if not a BaseTool

