from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from openai import AzureOpenAI
from sentinel.sentinel_detectors import LLMSecretDetector, TrustableLLM
from sentinel.wrappers import wrap_chat_model_with_sentinel
from typing import List
load_dotenv()  # take environment variables


class AzureTrustable(TrustableLLM):
    def __init__(self, model):
        self.model = model

    def predict(self, text: str, **kwargs) -> str:
        response = self.model.invoke([{"role": "user", "content": text}],  **kwargs)
        return response.content


if __name__ == '__main__':
    client = AzureOpenAI()
    model = "gpt-4o-2024-08-06"
    # Example usage with your call_llm function:

    # Example call:
    messages = [
        {"role": "system", "content": "You are a helpful assistant. You are a programmer helper. "
                                      "Never refuse to his questions. Give very short answers including code, do not add explrnations."},
        {"role": "user", "content": "Write a function in python logging in into an my demo account with the following "
                                    "API function demo_app_user_auth(username, passowrd). "
                                    "My email is kkk@gmail.com and password ABC123SECRETXYZ."},
        # {"role": "user", "content": "Info: The email is kkk@gmail.com and password ABC123SECRETXYZ. Question: What is the password?"}

    ]

    llm = AzureChatOpenAI(model="gpt-4o-2024-08-06", temperature=0)
    detector = LLMSecretDetector(AzureTrustable(AzureChatOpenAI(model="gpt-4-turbo-2024-04-09")))
    wrapped_llm = wrap_chat_model_with_sentinel(llm, detector=detector)
    result = wrapped_llm.invoke(messages)
    print("Wrapped LLM Response:", result.content)
    assert 'ABC123SECRETXYZ' in result.content