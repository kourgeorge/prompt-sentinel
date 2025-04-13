from copy import deepcopy
from typing import Any, Callable, Dict, Union, Tuple
from functools import wraps
from sentinel.sentinel_detectors import SecretDetector
from sentinel.session_context import SessionContext
from sentinel.vault import Vault  # Import Vault if needed elsewhere
import inspect
import asyncio
import uuid


try:
    from langchain.schema import AIMessage, HumanMessage, SystemMessage  # or BaseMessage

    def _process_langchain_message(
            message: Union[AIMessage, HumanMessage, SystemMessage],
            session_context: SessionContext
    ) -> Union[AIMessage, HumanMessage, SystemMessage]:
        # if getattr(message, "role", None) in {"tool", "tool_calls"}:
        #     return message

        kwargs: Dict[str, Any] = {
            "content": decode_text(message.content, session_context),
            "additional_kwargs": _process_response(message.additional_kwargs, session_context),
            "response_metadata": _process_response(message.response_metadata, session_context),
            "usage_metadata": _process_response(getattr(message, "usage_metadata", {}), session_context),
        }

        if isinstance(message, AIMessage):
            kwargs["tool_calls"] = _process_response(message.tool_calls, session_context)

        return message.copy(update=kwargs)
except ImportError:
    pass


def _sanitize_message(message: Any, session_context: SessionContext, detector: SecretDetector) -> Any:
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
                message["content"], session_context, detector
            )
        return message
    # Check for plain string.
    if hasattr(message, "content") and isinstance(getattr(message, "content"), str):
        sanitized_content = detect_and_encode_text(message.content, session_context, detector)
        try:
            # Attempt to create a new instance if the class accepts 'content'.
            return message.__class__(role=message.role, content=sanitized_content)
        except Exception:
            # Fallback: if instantiation fails, return a deepcopy with updated content.
            message = deepcopy(message)
            message.content = sanitized_content
            return message
    elif isinstance(message, str):
        return detect_and_encode_text(message, session_context, detector)
    # Check for list or tuple.
    elif isinstance(message, (list, tuple)):
        sanitized = []
        for item in message:
            sanitized.append(_sanitize_message(item, session_context, detector))
        return type(message)(sanitized)
    # Check if it has a 'content' attribute.

    else:
        # Fallback: convert to string.
        return detect_and_encode_text(str(message), session_context, detector)


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


def _process_dict(response: Dict[str, Any], session_context: SessionContext) -> Dict[str, Any]:
    if response.get("role") in {"tool", "tool_calls"}:
        return response

    result = deepcopy(response)

    if "content" in result and isinstance(result["content"], str):
        result["content"] = decode_text(result["content"], session_context)

    for key, value in result.items():
        result[key] = _process_response(value, session_context)

    return result


def _process_response(
        response: Any,
        session_context: SessionContext
) -> Any:
    if isinstance(response, list):
        return [_process_response(item, session_context) for item in response]

    if isinstance(response, dict):
        return _process_dict(response, session_context)

    if isinstance(response, str):
        return decode_text(response, session_context)

    try:
        if isinstance(response, (AIMessage, HumanMessage, SystemMessage)):
            return _process_langchain_message(response, session_context)
    except NameError:
        pass  # Either the message classes or function is not defined

    # require testing test
    if hasattr(response, '__dict__'):
        for attr in vars(response):
            value = getattr(response, attr)
            if isinstance(value, str):
                setattr(response, attr, decode_text(value, session_context))
            else:
                setattr(response, attr, _process_response(value, session_context))
        return response

    return response


def sentinel(
    detector: SecretDetector,
    session_context: SessionContext = None,  # Keep parameter for flexibility
    sanitize_arg: Union[int, str] = 0
) -> Callable:
    # Use the singleton SessionContext if none is provided
    session_context = session_context or SessionContext(
        project_token="default_token", server_url="http://default.server.url"
    )

    def decorator(func: Callable) -> Callable:

        def process_args(
            func: Callable,
            args: Tuple[Any, ...],
            kwargs: Dict[str, Any]
        ) -> Tuple[Tuple[Any, ...], Dict[str, Any]]:

            is_method = _is_likely_method(func)

            # Nothing to sanitize
            if not args and not kwargs:
                return args, kwargs

            if isinstance(sanitize_arg, int):
                idx = sanitize_arg + (1 if is_method else 0)
                if idx < len(args):
                    sanitized = deepcopy(args[idx])
                    sanitized = _sanitize_message(sanitized, session_context, detector)
                    args = args[(1 if inspect.ismethod(func) else 0):idx] + (sanitized,) + args[idx + 1:]
            elif isinstance(sanitize_arg, str):
                if sanitize_arg in kwargs:
                    sanitized = deepcopy(kwargs[sanitize_arg])
                    sanitized = _sanitize_message(sanitized, session_context, detector)
                    kwargs = dict(kwargs)
                    kwargs[sanitize_arg] = sanitized

            return args, kwargs

        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                args, kwargs = process_args(func, args, kwargs)
                response = await func(*args, **kwargs)
                return _process_response(response, session_context)
            return async_wrapper

        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                args, kwargs = process_args(func, args, kwargs)
                response = func(*args, **kwargs)
                return _process_response(response, session_context)
            return sync_wrapper

    return decorator


def report_to_server(prompt: str, secrets: list, sanitized_output: str, timestamp: str):
    """
    Sends a report about the detected secrets to the server.
    """
    url = "http://localhost:8000/api/report"
    payload = {
        "prompt": prompt,
        "secrets": secrets,
        "sanitized_output": sanitized_output,
        "timestamp": timestamp
    }
    try:
        requests.post(url, json=payload)
    except Exception:
        print("Could not send data to the server")

def detect_and_encode_text(
        text: str,
        session_context: SessionContext,
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
        placeholder = session_context.vault.add_secret_and_get_placeholder(secret["secret"])  # Use Vault to manage placeholder
        sanitized_text += placeholder
        last_idx = end
    sanitized_text += text[last_idx:]
    print(f"============================================"
          f"\n{len(secrets_info)} Secrets were detected in the LLM prompt."
          f"\nSanitized Input: {secret['secret']}\n"
          f"============================================")
    return sanitized_text


def decode_text(text: str, session_context: SessionContext) -> str:
    """
    Replace placeholders in the text with the original sensitive data.
    """
    secret_mapping = session_context.get_secret_mapping()  # Use Vault via SessionContext
    for placeholder, original in secret_mapping.items():
        text = text.replace(placeholder, original)
    return text


