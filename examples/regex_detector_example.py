from sentinel.sentinel_detectors import RegexSecretDetector
from sentinel import instrument_model_class, Vault

secret = 'AKIA1234567890ABCDEFGHIJKLM'

# This is a fake secret for testing purposes

class FakeChatModel:
    def invoke(self, messages):
        assert secret not in messages[0]["content"]
        return {"role": "assistant", "content": f"aws_provision_ec2({Vault._hash_secret(secret)})."}


if __name__ == '__main__':
    yaml_data = """
      aws_api_key: "AKIA[A-Z0-9]{20,60}"
      openai_api_key: 'sk\-[A-Za-z0-9]{15,30}'
      """

    # Create the detector using the YAML configuration
    detector = RegexSecretDetector(yaml_string=yaml_data)

    messages = [
        {"role": "user",
         "content": f"Call a AWS API to create an EC2 instance machine, (my key: {secret})" }
    ]

    wrapped_llm = instrument_model_class(FakeChatModel, detector)()
    response = wrapped_llm.invoke(messages)

    assert secret in response["content"]
