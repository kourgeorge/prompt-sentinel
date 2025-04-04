from langchain_community.chat_models import ChatOpenAI
from langchain_core.language_models import LanguageModelInput
from openai import AzureOpenAI

from prompt_sentinel import sentinel
from sentinel_detectors import LLMSecretDetector, OpenAITrustableLLM
from dotenv import load_dotenv

load_dotenv()


# Wrap the ChatOpenAI's invoke method using prompt_sentinel.
class SentinelChatOpenAI(ChatOpenAI):
    @sentinel(detector=LLMSecretDetector(OpenAITrustableLLM(AzureOpenAI(), "gpt-4o-2024-08-06")))
    def invoke(self, input: LanguageModelInput, **kwargs) -> str:
        # LangChain's ChatOpenAI expects messages as list of BaseMessage
        # Here we assume you're using raw dicts — convert them.
        from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

        # # Convert dicts to LangChain Message objects
        # formatted_msgs = []
        # for msg in messages:
        #     if msg["role"] == "system":
        #         formatted_msgs.append(SystemMessage(content=msg["content"]))
        #     elif msg["role"] == "user":
        #         formatted_msgs.append(HumanMessage(content=msg["content"]))
        #     elif msg["role"] == "assistant":
        #         formatted_msgs.append(AIMessage(content=msg["content"]))

        return super().invoke(input, **kwargs).content


# ✅ Example usage
if __name__ == "__main__":

    client = AzureOpenAI()
    model = "gpt-4o-2024-08-06"
    llm = SentinelChatOpenAI(model=model, temperature=0.0, max_tokens=400)

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": (
            "Write a function in python logging in into an my demo app account with the following API function demo_app_user_auth(username, passowrd). "
                    "My email is kkk@gmail.com and password ABC123SECRETXYZ."
        )}
    ]

    response = llm.invoke(messages)
    print("LLM Response:", response)
