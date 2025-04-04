from typing import List

from dotenv import load_dotenv
from openai import AzureOpenAI
from sentinel_detectors import ChatGPTSecretDetector
from prompt_sentinel import sentinel


@sentinel(detector=ChatGPTSecretDetector())
def call_llm(messages: List[dict]) -> str:
    """
    Call an LLM with a history of messages and return the response.
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.0,
            max_tokens=400,
            seed=123
        )
    except Exception as e:
        print(f"Error calling LLM: {e}.\nThe Messages: {messages}")
        return ""

    text_response = ""
    if response.choices:
        text_response = response.choices[0].message.content
    return text_response


if __name__ == '__main__':
    load_dotenv()  # take environment variables
    client = AzureOpenAI()
    model = "gpt-4o-2024-08-06"
    # Example usage with your call_llm function:

    # Example call:
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user",
         "content": "Write a function in python logging in into an my banck account with the following API function bank_user_auth(username, passowrd). "
                    "My email is kkk@gmail.com and password ABC123SECRETXYZ."},

    ]

    result = call_llm(messages)
    print("LLM Response:", result)
