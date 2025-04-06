from dotenv import load_dotenv
from langchain_community.chat_models import AzureChatOpenAI
from sentinel.sentinel_detectors import LLMSecretDetector
from sentinel.prompt_sentinel import sentinel

load_dotenv()  # take environment variables


@sentinel(detector=LLMSecretDetector(AzureChatOpenAI(model="gpt-4o-2024-08-06")))
def call_llm(messages: str) -> str:
    """
    Call an LLM with a history of messages and return the response.
    """
    print(f"LLM Received: {messages}")

    return "The password is __SECRET_2__"


if __name__ == '__main__':

    # Example call:
    llm_input = ("Info: The email is kkk@gmail.com and password ABC123SECRETXYZ. What is the password?")

    result = call_llm(llm_input)

    print("Decoded Output:", result)