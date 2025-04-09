import re
import yaml
import json
import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union, Callable
from functools import lru_cache
from sentinel.utils import extract_secrets_json


def find_secret_positions(text: str, secrets: List[str]) -> List[Dict]:
    """
    For each secret string, uses regex to find all occurrences in the text.
    Returns a list of dictionaries with keys "secret", "start", and "end".
    """
    results = []
    for secret in secrets:
        # Escape the secret to safely use in regex
        pattern = re.escape(secret)
        for match in re.finditer(pattern, text):
            results.append({
                "secret": secret,
                "start": match.start(),
                "end": match.end()
            })
    return results


# Base class for secret detectors.
class SecretDetector(ABC):
    @abstractmethod
    def detect(self, text: str) -> List[Dict]:
        """
        Detect sensitive secrets in the text.

        Should return a list of dictionaries with keys:
          - "secret": the detected secret text
          - "start": the start index of the secret in text
          - "end": the end index of the secret in text
        """
        pass


class TrustableLLM(ABC):
    @abstractmethod
    def predict(self, text: str, **kwargs) -> str:
        """Invoke the LLM with message(s) and optional keyword arguments."""
        pass


DEFAULT_PROMPT_TEMPLATE = (
    "Analyze the following text and extract only those pieces of information that are sensitive or private. "
    "Sensitive data includes API keys, passwords, tokens, sensitive personal information or any other information that could compromise security or safety if exposed. "
    "Do not include any data that is not sensitive. "
    "Do not extract already obfuscated tokens which follow the template '__SECRET_X__' (for example, '__SECRET_3__'). "
    "Return the result as a structured JSON output with the following schema: {{\"secrets\": [string, ...]}}.\n\n"
    "Text: ''' {text} '''"
)


class LLMSecretDetector(SecretDetector):
    def __init__(self,
                 trustable_llm,
                 prompt_format: Union[str, Callable[[str], str]] = DEFAULT_PROMPT_TEMPLATE
    ):
        """
        :param trustable_llm: An object with a method `predict(text: str) -> str`
        :param prompt_format: Either a string template with a '{text}' placeholder,
                              or a function that takes `text` and returns a prompt.
        """
        self.trustable_llm = trustable_llm
        self._cached_detect = self._build_cached_detect()
        self.prompt = prompt_format

    def _build_cached_detect(self):
        @lru_cache(maxsize=128)
        def _detect(text: str) -> List[Dict[str, Any]]:

            formatted_prompt = self.prompt.format(text=text)
            try:
                response_text = self.trustable_llm.predict(formatted_prompt)
            except Exception as e:
                print(f"Error calling LLM: {e}")
                return []

            try:
                json_dict = extract_secrets_json(response_text)
                secret_list = json_dict['secrets']
                if not isinstance(secret_list, list):
                    print("LLM did not return a list. Response:", response_text)
                    return []
            except json.JSONDecodeError:
                print("Failed to decode LLM response as JSON. Response:", response_text)
                return []

            return find_secret_positions(text, secret_list)

        return _detect

    def detect(self, text: str) -> List[Dict[str, Any]]:
        return self._cached_detect(text)

    def report_cache(self):
        return self._cached_detect.cache_info()


class PythonStringDataDetector(SecretDetector):
    # from high_entropy_string import PythonStringData
    MIN_CONFIDENCE_THRESHOLD = 3
    MIN_SEVERITY_THRESHOLD = 3

    def __init__(self, confidence_threshold: int = MIN_CONFIDENCE_THRESHOLD,
                 severity_threshold: int = MIN_SEVERITY_THRESHOLD):
        self.confidence_threshold = confidence_threshold
        self.severity_threshold = severity_threshold
        # Build a cached detection function bound to this instance.
        self._cached_detect = self._build_cached_detect()

    def _build_cached_detect(self):
        """
        Returns a function that performs secret detection by analyzing each token in the text
        using PythonStringData, and caches the results with lru_cache. The cache key will be the text input.
        """
        from pkgs.high_entropy_strings import PythonStringData
        @lru_cache(maxsize=128)
        def _detect(text: str) -> List[Dict]:
            results = []
            # Tokenize the text using a simple regex.
            for match in re.finditer(r'\b\S+\b', text):
                token = match.group(0)
                # Create a PythonStringData instance for the token.
                psd = PythonStringData(
                    string=token,
                    target=token,  # In this simple example, target is the same as the token.
                    caller="PythonStringDataDetector"
                )
                # Decide if the token qualifies as a secret.
                # Here we flag the token if either its confidence or severity is above threshold.
                if psd.confidence >= self.confidence_threshold or psd.severity >= self.severity_threshold:
                    results.append({
                        "secret": token,
                        "start": match.start(),
                        "end": match.end()
                    })
            return results

        return _detect

    def detect(self, text: str) -> List[Dict]:
        """
        Uses the cached detection function to get the list of potential secrets.
        Each detected secret is a dict with keys: "secret", "start", and "end".
        """
        return self._cached_detect(text)

    def report_cache(self):
        """
        Prints and returns the cache info and, if possible, the cached items.
        Note: Accessing the internal cache is relying on CPython internals.
        """
        # Print cache statistics.
        cache_info = self._cached_detect.cache_info()
        print("Cache info:", cache_info)
        # Try to inspect the raw cache.
        try:
            cache = self._cached_detect.cache
            print("Cached items:", dict(cache))
        except AttributeError:
            print("Direct cache inspection not supported on this Python version.")
        return cache_info


class RegexSecretDetector(SecretDetector):
    def __init__(self, yaml_path: Optional[str] = None):
        """
        :param pattern_config: Optional dict of secret types to regex patterns
        :param yaml_path: Optional path to YAML file with secret type regex patterns
        """
        if yaml_path:
            pattern_config = self._load_patterns_from_yaml(yaml_path)
        else:
            current_dir = os.path.dirname(__file__)
            yaml_path = os.path.join(current_dir, 'basic_secret_patterns.yaml')
            pattern_config = self._load_patterns_from_yaml(yaml_path)

        self.patterns = {key: re.compile(pattern) for key, pattern in pattern_config.items()}

    @staticmethod
    def _load_patterns_from_yaml(path: str) -> Dict[str, str]:
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            raise ValueError("YAML file must contain a dictionary mapping secret types to regex strings.")
        return data

    def detect(self, text: str) -> List[Dict]:
        detected = []
        for secret_type, pattern in self.patterns.items():
            for match in pattern.finditer(text):
                detected.append({
                    "secret": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                    "type": secret_type
                })
        return detected


class DummyDetector(SecretDetector):
    def detect(self, text: str) -> List[Dict]:
        """
        A dummy detector that does nothing and returns an empty list.
        """
        return []


try:
    from langchain.output_parsers import ResponseSchema, StructuredOutputParser

    class LangchainLLMSecretDetector(SecretDetector):
        def __init__(self, trustable_llm):
            """
            :param trustable_llm: An object with a method `chat(messages: List[Dict[str, str]], temperature: float, max_tokens: int) -> str`
            """
            self.trustable_llm = trustable_llm
            self._cached_detect = self._build_cached_detect()
            response_schemas = [
                ResponseSchema(name="secrets", description="A list of sensitive or private data extracted from the text")
            ]
            self.output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

        def _build_cached_detect(self):
            @lru_cache(maxsize=128)
            def _detect(text: str) -> List[Dict]:
                prompt = (
                    "Analyze the following text and extract only those pieces of information that are sensitive or private. "
                    "Sensitive data includes API keys, passwords, tokens, sensitive personal information or any other information that could compromise security or safety if exposed. "
                    "Do not include any data that is not sensitive. "
                    "Do not extract already obfuscated tokens which follow the template '__SECRET_X__' (for example, '__SECRET_3__'). "
                    "Return the result as a structured JSON output with the following schema: {\"secrets\": [string, ...]}.\n\n"
                    f"{self.output_parser.get_format_instructions()}\n\n"
                    f"Text: '''{text}'''"
                )

                try:
                    response_text = self.trustable_llm.predict(
                        text=prompt,
                    )
                except Exception as e:
                    print(f"Error calling LLM: {e}")
                    return []

                try:
                    parsed_output = self.output_parser.parse(str(response_text))
                    secret_list = parsed_output.get("secrets", [])
                    # secret_list = parse_json_output(response_text)
                    if not isinstance(secret_list, list):
                        print("LLM did not return a list. Response:", response_text)
                        return []
                except json.JSONDecodeError:
                    print("Failed to decode LLM response as JSON. Response:", response_text)
                    return []

                return find_secret_positions(text, secret_list)

            return _detect

        def detect(self, text: str) -> List[Dict]:
            return self._cached_detect(text)

        def report_cache(self):
            return self._cached_detect.cache_info()

except ImportError:
    LLMSecretDetectorLangchain = None