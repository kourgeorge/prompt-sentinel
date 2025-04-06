from copy import deepcopy
from typing import Any, Callable
from functools import wraps
from sentinel.sentinel_detectors import SecretDetector
import inspect
import asyncio
from langchain.schema import AIMessage, HumanMessage, SystemMessage  # or BaseMessage
from sentinel.secret_context import set_secret_mapping


def _sanitize_message(message: Any, secret_mapping: dict, token_counter: list, detector: SecretDetector) -> Any:
    """
    Sanitizes a single message-like representation.
    - If it's a string, sanitize the text.
    - If it's a dict with a "content" key, sanitize that content.
    - If it's a list or tuple of strings, sanitize each string.
    - If it has a 'content' attribute (e.g., HumanMessage), create a new message with sanitized content.
    - Otherwise, fallback to converting to string and sanitizing.
    """
    # Check for dict with "content" key.
    if isinstance(message, dict):
        if "content" in message and isinstance(message["content"], str):
            message["content"] = detect_and_encode_text(
                message["content"], secret_mapping, token_counter, detector
            )
        return message
    # Check for plain string.
    if hasattr(message, "content") and isinstance(getattr(message, "content"), str):
        sanitized_content = detect_and_encode_text(message.content, secret_mapping, token_counter, detector)
        try:
            # Attempt to create a new instance if the class accepts 'content'.
            return message.__class__(role=message.role, content=sanitized_content)
        except Exception:
            # Fallback: if instantiation fails, return a deepcopy with updated content.
            message = deepcopy(message)
            message.content = sanitized_content
            return message
    elif isinstance(message, str):
        return detect_and_encode_text(message, secret_mapping, token_counter, detector)
    # Check for list or tuple.
    elif isinstance(message, (list, tuple)):
        sanitized = []
        for item in message:
            sanitized.append(_sanitize_message(item, secret_mapping, token_counter, detector))
        return type(message)(sanitized)
    # Check if it has a 'content' attribute.

    else:
        # Fallback: convert to string.
        return detect_and_encode_text(str(message), secret_mapping, token_counter, detector)


def _is_likely_method(func: Callable) -> bool:
    """Heuristically check if this is an instance or class method."""
    if inspect.ismethod(func):
        return True  # bound method
    qualname_parts = getattr(func, "__qualname__", "").split(".")
    if len(qualname_parts) > 1:
        try:
            sig = inspect.signature(func)
            first_param = list(sig.parameters.values())[0].name
            return first_param in {"self", "cls"}
        except Exception:
            return False
    return False


def _process_response(response, secret_mapping):
    # If response is a list, process each element recursively.
    if isinstance(response, list):
        return [_process_response(item, secret_mapping) for item in response]

    # If response is a dict, decode 'content' and process nested values.
    if isinstance(response, dict):
        role = response.get("role")
        if role in {"tool", "tool_calls"}:
            return response
        response = deepcopy(response)
        if "content" in response:
            response["content"] = decode_text(response["content"], secret_mapping)
        for key, value in response.items():
            response[key] = _process_response(value, secret_mapping)
        return response

    # If it's a LangChain message (e.g., AIMessage)
    if isinstance(response, (AIMessage, HumanMessage, SystemMessage)):
        if getattr(response, "role", None) in {"tool", "tool_calls"}:
            return response

        sanitized_content = decode_text(response.content, secret_mapping)
        sanitized_kwargs = _process_response(response.additional_kwargs, secret_mapping)
        sanitized_meta = _process_response(response.response_metadata, secret_mapping)
        sanitized_usage = _process_response(getattr(response, "usage_metadata", {}), secret_mapping)

        if isinstance(response, AIMessage):
            sanitized_tool_calls = _process_response(response.tool_calls, secret_mapping)
            return response.copy(update={
                "content": sanitized_content,
                "additional_kwargs": sanitized_kwargs,
                "response_metadata": sanitized_meta,
                "usage_metadata": sanitized_usage,
                "tool_calls": sanitized_tool_calls
            })

        return response.copy(update={
            "content": sanitized_content,
            "additional_kwargs": sanitized_kwargs,
            "response_metadata": sanitized_meta,
            "usage_metadata": sanitized_usage,
        })

    # If it's a string, decode it
    if isinstance(response, str):
        return decode_text(response, secret_mapping)

    # Fallback: return as is
    return response


def sentinel(detector: SecretDetector):
    def decorator(func: Callable, ):
        is_method = _is_likely_method(func)

        # Helper to sanitize arguments
        def process_args(args):
            secret_mapping = {}
            token_counter = [1]
            # If there are no args, nothing to do.
            if not args:
                return args, secret_mapping

            # Assume that for methods, args[0] is self and args[1] is input
            if is_method:
                input_data = args[1]
                sanitized_input = deepcopy(input_data)
                sanitized_input = _sanitize_message(sanitized_input, secret_mapping, token_counter, detector)
                new_args = (sanitized_input,) + args[2:]
            else:
                input_data = args[0]
                sanitized_input = deepcopy(input_data)
                sanitized_input = _sanitize_message(sanitized_input, secret_mapping, token_counter, detector)
                new_args = (sanitized_input,) + args[1:]
            return new_args, secret_mapping

        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                if not args:
                    response = await func(*args, **kwargs)
                    return _process_response(response, {})
                new_args, secret_mapping = process_args(args)
                response = await func(*new_args, **kwargs)
                return _process_response(response, secret_mapping)

            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                if not args:
                    return func(*args, **kwargs)
                new_args, secret_mapping = process_args(args)
                response = func(*new_args, **kwargs)
                return _process_response(response, secret_mapping)

            return sync_wrapper

    return decorator


def detect_and_encode_text(
        text: str,
        secret_mapping: dict,
        token_counter: list,
        detector: SecretDetector
) -> str:
    """
    Uses the provided SecretDetector to find sensitive data in the text
    and replace it with tokens.
    """
    secrets_info = detector.detect(text)
    if not secrets_info:
        return text

    # Sort detected secrets by their start index for proper replacement.
    secrets_info.sort(key=lambda x: x["start"])
    sanitized_text = ""
    last_idx = 0
    for secret in secrets_info:
        start, end = secret["start"], secret["end"]
        sanitized_text += text[last_idx:start]
        token = f"__SECRET_{token_counter[0]}__"
        secret_mapping[token] = secret["secret"]
        token_counter[0] += 1
        sanitized_text += token
        last_idx = end
    sanitized_text += text[last_idx:]
    set_secret_mapping(secret_mapping)
    return sanitized_text


def decode_text(text: str, secret_mapping: dict) -> str:
    """
    Replace tokens in the text with the original sensitive data.
    """
    for token, original in secret_mapping.items():
        text = text.replace(token, original)
    return text
