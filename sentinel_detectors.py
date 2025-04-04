import json
import re
from abc import ABC, abstractmethod
from typing import List, Dict
import requests
from openai import AzureOpenAI
from utils import parse_json_output
from functools import lru_cache
from high_entropy_string import PythonStringData



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


def call_ollama(prompt: str) -> str:
    """
    Call the Ollama local LLM with the provided prompt.

    Replace the URL, model, and parameters with your actual configuration.
    """
    url = "http://localhost:11434/api/v1/generate"  # Example endpoint; update as needed.
    payload = {
        "prompt": prompt,
        "model": 'llama3.2',  # Replace with your Ollama model name.
        "temperature": 0.0,
        "max_tokens": 150,
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"Error calling Ollama: {e}")
        return ""
    return response.text


class OllamaSecretDetector(SecretDetector):
    def detect(self, text: str) -> List[Dict]:
        """
        Uses Ollama to detect secrets in the text.

        The prompt instructs Ollama to return a JSON array of detected secrets,
        where each secret is a JSON object with "secret", "start", and "end" keys.

        Example output:
        [
            {"secret": "API key 12345", "start": 10, "end": 24},
            {"secret": "password", "start": 50, "end": 58}
        ]
        """
        prompt = (
            "Analyze the following text and extract any sensitive or private data (secrets). "
            "Return the result as a JSON array where each element is an object with keys "
            "'secret', 'start', and 'end' indicating the text of the secret and its position in the text. "
            f"Text: '''{text}'''"
        )
        ollama_response = call_ollama(prompt)
        try:
            # Expecting Ollama to return a JSON string.
            secrets = json.loads(ollama_response)
            if isinstance(secrets, list):
                return secrets
            else:
                print("Ollama did not return a list. Response:", ollama_response)
                return []
        except json.JSONDecodeError:
            print("Failed to decode Ollama response as JSON. Response:", ollama_response)
            return []


class ChatGPTSecretDetector(SecretDetector):
    def __init__(self):
        self.client = AzureOpenAI()
        self.model = "gpt-4o-2024-08-06"
        # Build a cached detection function bound to this instance.
        self._cached_detect = self._build_cached_detect()

    def _build_cached_detect(self):
        """
        Returns a function that performs detection using the ChatGPT API,
        and caches the results using lru_cache. The cache key will be the text input.
        """
        @lru_cache(maxsize=128)
        def _detect(text: str) -> List[Dict]:
            prompt = (
                "Analyze the following text and extract only those pieces of information that are sensitive or private. "
                "Sensitive data includes API keys, passwords, tokens, or any other information that could compromise security if exposed. "
                "Do not include any data that is not sensitive. "
                "Do not extract already obfuscated tokens which follow the template '__SECRET_d__' (for example, '__SECRET_3__'). "
                "Return the result as a JSON array of strings, where each string is exactly the sensitive data as it appears in the text. "
                "If no sensitive data is found, return an empty JSON array.\n\n"
                f"Text: '''{text}'''"
            )
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0,
                    max_tokens=150,
                )
            except Exception as e:
                print(f"Error calling ChatGPT API: {e}")
                return []

            response_text = response.choices[0].message.content
            try:
                # Parse the response to get a list of secret strings.
                secret_list = parse_json_output(response_text)
                if not isinstance(secret_list, list):
                    print("ChatGPT did not return a list. Response:", response_text)
                    return []
            except json.JSONDecodeError:
                print("Failed to decode ChatGPT response as JSON. Response:", response_text)
                return []

            # Find the positions of each secret in the original text.
            secret_positions = find_secret_positions(text, secret_list)
            return secret_positions

        return _detect

    def detect(self, text: str) -> List[Dict]:
        """
        Uses the cached detection function to get sensitive secret positions.
        """
        return self._cached_detect(text)

    def report_cache(self):
        print(self._cached_detect.cache)
        return self._cached_detect.cache_info()


class PythonStringDataDetector(SecretDetector):
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


# Example usage:
if __name__ == "__main__":
    sample_text = (
        "User login: password: SuperSecret123, API key: ABCD-1234-EFGH-5678, "
        "and token: TOKEN9876XYZ. This function call is safe: apis.supervisor.show_account_passwords()"
    )
    detector = PythonStringDataDetector()
    detected_secrets = detector.detect(sample_text)

    import json

    print("Detected potential secrets:")
    print(json.dumps(detected_secrets, indent=2))

    # Optionally, report cache information.
    detector.report_cache()
