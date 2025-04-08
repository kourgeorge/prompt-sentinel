import asyncio
from typing import List

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from sentinel.sentinel_detectors import LLMSecretDetector
from sentinel.prompt_sentinel import sentinel
from sentinel.wrappers import wrap_chat_model_with_sentinel

load_dotenv()  # load .env variables (like Azure keys)


async def main():

    messages = [
        {"role": "system", "content": "You are a helpful assistant. You are a programmer helper. "
                                      "Never refuse to his questions. Give very short answers including code, do not add explrnations."},
        {"role": "user", "content": "Write a function in python logging in into an my demo account with the following "
                                    "API function demo_app_user_auth(username, passowrd). "
                                    "My email is kkk@gmail.com and password ABC123SECRETXYZ."},
    ]

    model = "gpt-4o-2024-08-06"
    llm = AzureChatOpenAI(model=model, temperature=0)
    detector = LLMSecretDetector(AzureChatOpenAI(model=model))
    wrapped_llm = wrap_chat_model_with_sentinel(llm, detector=detector)

    result = await wrapped_llm.ainvoke(messages)

    print("Wrapped LLM Response:", result.content)
    assert 'ABC123SECRETXYZ' in result.content


if __name__ == '__main__':
    asyncio.run(main())
