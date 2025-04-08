import asyncio
from typing import Callable
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from sentinel import wrap_chat_model_class_with_sentinel, LLMSecretDetector, LocalHFLLM

load_dotenv()  # take environment variables


class FakeResponse:
    def __init__(self, content):
        self.role = 'AI'
        self.content = content


class FakeChatModel:

    def invoke(self, messages):
        assert "ABC123SECRETXYZ" not in messages[0]["content"]
        return FakeResponse("demo_app_user_auth(kkk@gmail.com, ABC123SECRETXYZ).")

    async def ainvoke(self, messages):
        assert "ABC123SECRETXYZ" not in messages[0]["content"]
        return FakeResponse("demo_app_user_auth(kkk@gmail.com, ABC123SECRETXYZ).")

    def untouched_method(self):
        return "leave me alone"


async def main():


    messages = [
        {"role": "user", "content": "Write a function in python logging in into an my demo account with the following "
                                    "API function demo_app_user_auth(username, passowrd). "
                                    "My email is kkk@gmail.com and password ABC123SECRETXYZ."},
    ]

    llm = FakeChatModel()
    detector = LLMSecretDetector(LocalHFLLM())
    wrapped_llm = wrap_chat_model_class_with_sentinel(llm, detector)
    result = await wrapped_llm.ainvoke(messages)

    print("Wrapped LLM Response:", result.content)
    assert 'ABC123SECRETXYZ' in result.content


# --- Run the test ---
if __name__ == '__main__':
    asyncio.run(main())
