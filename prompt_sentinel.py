from copy import deepcopy
from typing import List, Any, Callable
from functools import wraps
from sentinel_detectors import SecretDetector
from utils import parse_json_output


# MessageLikeRepresentation is defined as:
# Union[BaseMessage, list[str], tuple[str, str], str, dict[str, Any]]
# We'll try to handle each of these cases.

def _sanitize_message(
        message: Any,
        secret_mapping: dict,
        token_counter: list,
        detector: SecretDetector
) -> Any:
    """
    Sanitizes a single message-like representation.
    - If it's a string, sanitize the text.
    - If it's a dict with a "content" key, sanitize that content.
    - If it's a list or tuple of strings, sanitize each string.
    - If it's an instance of BaseMessage (from langchain.schema), create a new message with sanitized content.
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
    elif isinstance(message, str):
        return detect_and_encode_text(message, secret_mapping, token_counter, detector)
    # Check for list or tuple.
    elif isinstance(message, (list, tuple)):
        # Assume it's a sequence of strings or message-like items.
        sanitized = []
        for item in message:
            sanitized.append(_sanitize_message(item, secret_mapping, token_counter, detector))
        # Preserve original type.
        return type(message)(sanitized)
    else:
        # Try to check if it's a BaseMessage (e.g., from langchain.schema).
        try:
            from langchain.schema import BaseMessage
            if isinstance(message, BaseMessage):
                # Create a copy of the message with sanitized content.
                sanitized_content = detect_and_encode_text(message.content, secret_mapping, token_counter, detector)
                # Assume the message class accepts a "content" argument.
                return message.__class__(content=sanitized_content)
        except ImportError:
            pass
        # Fallback: convert to string.
        return detect_and_encode_text(str(message), secret_mapping, token_counter, detector)


def sentinel(detector: SecretDetector):
    """
    Decorator factory that creates a decorator which sanitizes any LanguageModelInput
    (matching the MessageLikeRepresentation union) before calling the LLM function
    and decodes the response after.

    This version works with both standalone functions and instance methods.
    """

    def decorator(func:Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Determine if the function is bound (i.e., first arg is self)
            if args and hasattr(args[0], '__class__'):
                self_instance = args[0]
                input_data = args[1]
                new_input = deepcopy(input_data)
                new_args = (self_instance, new_input) + args[2:]
            else:
                input_data = args[0]
                new_input = deepcopy(input_data)
                new_args = (new_input,) + args[1:]

            secret_mapping = {}
            token_counter = [1]

            # Sanitize the input based on its type.
            new_input = _sanitize_message(new_input, secret_mapping, token_counter, detector)

            # Update new_args with the sanitized input.
            if args and hasattr(args[0], '__class__'):
                new_args = (args[0], new_input) + args[2:]
            else:
                new_args = (new_input,) + args[1:]

            # Call the original function with sanitized input.
            response_text = func(*new_args, **kwargs)

            # Post-process: decode the tokens in the response.
            return decode_text(response_text, secret_mapping)

        return wrapper

    return decorator


# --- Helper functions (unchanged) ---

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
    return sanitized_text


def decode_text(text: str, secret_mapping: dict) -> str:
    """
    Replace tokens in the text with the original sensitive data.
    """
    for token, original in secret_mapping.items():
        text = text.replace(token, original)
    return text
