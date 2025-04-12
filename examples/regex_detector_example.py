from sentinel.sentinel_detectors import RegexSecretDetector
from sentinel import instrument_model_class


class FakeResponse:
    def __init__(self, content):
        self.role = 'AI'
        self.content = content


class FakeChatModel:
    def invoke(self, messages):
        assert "sk-abcdefghijklmnopqrstuvwxyzABCDEFGH" not in messages[0]["content"]
        return FakeResponse("aws_provision_machine_with_open_ai(__SECRET_1__).")

def main():
    yaml_data = """
      aws_api_key: "AKIA[A-Z0-9]{15,16}"
      openai_api_key: 'sk\-[A-Za-z0-9]{34}'
      """

    # Create the detector using the YAML configuration
    detector = RegexSecretDetector(yaml_string=yaml_data)

    messages = [
        {"role": "user", "content": "Call a create instance machine on AWS, (my key AKIA1234567890ABCDE) and use openAI Interface"
                                    "Use the token is sk-abcdefghijklmnopqrstuvwxyzABCDEFGH. "
                                    "These should both be detected."},
    ]


    wrapped_llm = instrument_model_class(FakeChatModel, detector)()
    result = wrapped_llm.invoke(messages)

    print("Wrapped LLM Response:", result.content)
    assert 'AKIA1234567890ABCDE' in result.content


# --- Run the test ---
if __name__ == '__main__':
    main()
