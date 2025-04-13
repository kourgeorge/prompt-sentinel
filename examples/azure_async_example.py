import asyncio
from typing import List

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from sentinel.sentinel_detectors import LLMSecretDetector
from sentinel.prompt_sentinel import sentinel
from sentinel.wrappers import instrument_model_class

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
    detector = LLMSecretDetector(AzureChatOpenAI(model=model))
    InstrumentedAzureOpenAI = instrument_model_class(AzureChatOpenAI, detector=detector)
    wrapped_llm = InstrumentedAzureOpenAI(model=model, temperature=0)

    result = await wrapped_llm.ainvoke(messages)

    print("Wrapped LLM Response:", result.content)
    assert 'ABC123SECRETXYZ' in result.content


if __name__ == '__main__':
    asyncio.run(main())
