from sentinel.sentinel_detectors import RegexSecretDetector
from sentinel import instrument_model_class

class FakeChatModel:
    def invoke(self, messages):
        assert "sk-abcdefghijklmnopqrstuvwxyzABCDEFGH" not in messages[0]["content"]
        return {"role": "assistant", "content": "aws_provision_machine_with_open_ai(__SECRET_1__)."}

if __name__ == '__main__':

    yaml_data = """
      aws_api_key: "AKIA[A-Z0-9]{20,60}"
      openai_api_key: 'sk\-[A-Za-z0-9]{15,30}'
      """

    # Create the detector using the YAML configuration
    detector = RegexSecretDetector(yaml_string=yaml_data)

    messages = [
        {"role": "user",
         "content": "Call a create instance machine on AWS, (my key AKIA1234567890ABCDEFGHIJKLM) and use openAI Interface"
                    "Use the token is sk-abcdefghijklmnopqrstuvwxyzABCDEFGH. "
                    "These should both be detected."},
    ]

    wrapped_llm = instrument_model_class(FakeChatModel, detector)()
    response = wrapped_llm.invoke(messages)

    assert 'AKIA1234567890ABCDEFGHIJKLM' in response["content"]