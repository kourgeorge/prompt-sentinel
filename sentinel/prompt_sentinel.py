from copy import deepcopy
from typing import Any, Callable, Dict, Union, Tuple
from functools import wraps
from sentinel.sentinel_detectors import SecretDetector
import inspect
import asyncio
from sentinel.secret_context import set_secret_mapping


try:
    from langchain.schema import AIMessage, HumanMessage, SystemMessage  # or BaseMessage

    def _process_langchain_message(
            message: Union[AIMessage, HumanMessage, SystemMessage],
            secret_mapping: Dict[str, str]
    ) -> Union[AIMessage, HumanMessage, SystemMessage]:
        # if getattr(message, "role", None) in {"tool", "tool_calls"}:
        #     return message

        kwargs: Dict[str, Any] = {
            "content": decode_text(message.content, secret_mapping),
            "additional_kwargs": _process_response(message.additional_kwargs, secret_mapping),
            "response_metadata": _process_response(message.response_metadata, secret_mapping),
            "usage_metadata": _process_response(getattr(message, "usage_metadata", {}), secret_mapping),
        }

        if isinstance(message, AIMessage):
            kwargs["tool_calls"] = _process_response(message.tool_calls, secret_mapping)

        return message.copy(update=kwargs)
except ImportError:
    pass


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


def _process_dict(response: Dict[str, Any], secret_mapping: Dict[str, str]) -> Dict[str, Any]:
    if response.get("role") in {"tool", "tool_calls"}:
        return response

    result = deepcopy(response)

    if "content" in result and isinstance(result["content"], str):
        result["content"] = decode_text(result["content"], secret_mapping)

    for key, value in result.items():
        result[key] = _process_response(value, secret_mapping)

    return result


def _process_response(
        response: Any,
        secret_mapping: Dict[str, str]
) -> Any:
    if isinstance(response, list):
        return [_process_response(item, secret_mapping) for item in response]

    if isinstance(response, dict):
        return _process_dict(response, secret_mapping)

    if isinstance(response, str):
        return decode_text(response, secret_mapping)

    try:
        if isinstance(response, (AIMessage, HumanMessage, SystemMessage)):
            return _process_langchain_message(response, secret_mapping)
    except NameError:
        pass  # Either the message classes or function is not defined

    # require testing test
    if hasattr(response, '__dict__'):
        for attr in vars(response):
            value = getattr(response, attr)
            if isinstance(value, str):
                setattr(response, attr, decode_text(value, secret_mapping))
            else:
                setattr(response, attr, _process_response(value, secret_mapping))
        return response

    return response


def sentinel(
    detector: SecretDetector,
    sanitize_arg: Union[int, str] = 0
) -> Callable:
    def decorator(func: Callable) -> Callable:

        def process_args(
            func: Callable,
            args: Tuple[Any, ...],
            kwargs: Dict[str, Any]
        ) -> Tuple[Tuple[Any, ...], Dict[str, Any], Dict[str, str]]:
            secret_mapping: Dict[str, str] = {}
            token_counter = [1]

            is_method = _is_likely_method(func)

            # Nothing to sanitize
            if not args and not kwargs:
                return args, kwargs, secret_mapping

            if isinstance(sanitize_arg, int):
                idx = sanitize_arg + (1 if is_method else 0)
                if idx < len(args):
                    sanitized = deepcopy(args[idx])
                    sanitized = _sanitize_message(sanitized, secret_mapping, token_counter, detector)
                    args = args[(1 if inspect.ismethod(func) else 0):idx] + (sanitized,) + args[idx + 1:] #do not pass  self.
            elif isinstance(sanitize_arg, str):
                if sanitize_arg in kwargs:
                    sanitized = deepcopy(kwargs[sanitize_arg])
                    sanitized = _sanitize_message(sanitized, secret_mapping, token_counter, detector)
                    kwargs = dict(kwargs)
                    kwargs[sanitize_arg] = sanitized

            return args, kwargs, secret_mapping

        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                args, kwargs, secret_mapping = process_args(func, args, kwargs)
                response = await func(*args, **kwargs)
                return _process_response(response, secret_mapping)
            return async_wrapper

        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                args, kwargs, secret_mapping = process_args(func, args, kwargs)
                response = func(*args, **kwargs)
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
    print(f"============================================"
          f"\n{len(secrets_info)} Secrets were detected in the LLM prompt."
          f"\nSanitized Input: {secret['secret']}\n"
          f"============================================")
    return sanitized_text


def decode_text(text: str, secret_mapping: dict) -> str:
    """
    Replace tokens in the text with the original sensitive data.
    """
    for token, original in secret_mapping.items():
        text = text.replace(token, original)
    return text
