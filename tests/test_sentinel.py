import pytest
from sentinel.prompt_sentinel import sentinel, decode_text
from typing import List, Dict, Any
from sentinel.sentinel_detectors import SecretDetector


# Dummy SecretDetector that flags certain strings as secrets
class TestDummyDetector(SecretDetector):
    def detect(self, text: str) -> List[Dict[str, Any]]:
        # Detect a few hardcoded test secrets
        test_secrets = ["apikey-xyz789", "john.doe@example.com", "4111 1111 1111 1111"]
        for secret in test_secrets:
            start = text.find(secret)
            if start != -1:
                return [{
                    "start": start,
                    "end": start + len(secret),
                    "secret": secret
                }]
        return []


# --- Tests ---

@sentinel(detector=TestDummyDetector())
def echo_string(msg: str) -> str:
    # Ensure the message no longer contains raw secrets
    assert "apikey" not in msg and "example.com" not in msg
    return f"Echo: {msg}"


def test_echo_string():
    input_text = "My key is apikey-xyz789"
    output = echo_string(input_text)
    assert "apikey-xyz789" in output
    assert "__SECRET_" not in output


@sentinel(detector=TestDummyDetector())
def process_messages(messages: List[Dict[str, str]]) -> str:
    for m in messages:
        assert "example.com" not in m["content"]
    return f"Processed: {[m['content'] for m in messages]}"


def test_process_messages():
    messages = [{"role": "user", "content": "Email me at john.doe@example.com"}]
    result = process_messages(messages)
    assert "john.doe@example.com" in result
    assert "__SECRET_" not in result


class DummyLLMStaticMethod:
    @staticmethod
    @sentinel(detector=TestDummyDetector())
    def chat(messages: List[Dict[str, str]]) -> str:
        for m in messages:
            assert "apikey" not in m["content"]
        return messages[0]['content']


class DummyLLM:
    @sentinel(detector=TestDummyDetector())
    def chat(self, messages: List[Dict[str, str]]) -> str:
        for m in messages:
            assert "apikey" not in m["content"]
        return messages[0]['content']


def test_class_method():
    llm = DummyLLM()
    response = llm.chat([{"role": "user", "content": "apikey-xyz789"}])
    assert "apikey-xyz789" in response


@sentinel(detector=TestDummyDetector())
def fake_llm(messages: List[Dict[str, str]]) -> str:
    # Return the obfuscated token in response — decorator should decode it
    return "Token: __SECRET_1__"


def test_output_decoding():
    input_messages = [{"role": "user", "content": "4111 1111 1111 1111"}]
    out = fake_llm(input_messages)
    assert "4111 1111 1111 1111" in out
    assert "__SECRET_" not in out


@sentinel(detector=TestDummyDetector())
def nested_input(input: Any) -> str:
    return str(input)


def test_nested_input():
    input_data = ["test", ("another", "john.doe@example.com")]
    out = nested_input(input_data)
    assert "john.doe@example.com" in out
    assert "__SECRET_" not in out
