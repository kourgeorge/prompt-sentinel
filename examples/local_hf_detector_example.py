import asyncio
from transformers import pipeline
import os
from sentinel import instrument_model_class, LLMSecretDetector, TrustableLLM


class LocalHFLLM(TrustableLLM):
    def __init__(self, model_name: str = 'Qwen/Qwen2.5-1.5B-Instruct', token=os.getenv('HUGGING_FACE_HUB_TOKEN')):
        self.generator = pipeline("text-generation", model=model_name, device=0, token=token)

    def predict(self, text: str, **kwargs) -> str:
        outputs = self.generator(text, max_new_tokens=512, do_sample=False, temperature=0)
        full_output = outputs[0]['generated_text']
        # Remove the input prompt from the beginning
        generated_part = full_output[len(text):].strip()
        return generated_part


class FakeChatModel:

    def invoke(self, messages):
        assert "ABC123SECRETXYZ" not in messages[0]["content"]
        return {"role": "ai", "content": "demo_app_user_auth(kkk@gmail.com, __SECRET_1__)."}

    async def ainvoke(self, messages):
        assert "ABC123SECRETXYZ" not in messages[0]["content"]
        return {"role": "ai", "content": "demo_app_user_auth(kkk@gmail.com, __SECRET_1__)."}


async def main():
    messages = [
        {"role": "user", "content": "Write a function in python logging in into an my demo account with the following "
                                    "API function demo_app_user_auth(username, passowrd). "
                                    "My email is kkk@gmail.com and password ABC123SECRETXYZ."},
    ]

    custom_prompt = (
        "Extract secrets from the following:\n\n"
        "Only include API keys, secrets, tokens, or credentials. Use the folloeing output format as JSON: {{\"secrets\": [...]}}\n\n"
        "Text: {text}"
    )

    detector = LLMSecretDetector(LocalHFLLM(model_name='Qwen/Qwen2.5-1.5B-Instruct'), prompt_format=custom_prompt)
    wrapped_llm = instrument_model_class(FakeChatModel, detector)()
    result = await wrapped_llm.ainvoke(messages)

    print("Wrapped LLM Response:", result.content)
    assert 'ABC123SECRETXYZ' in result.content


# --- Run the test ---
if __name__ == '__main__':
    asyncio.run(main())
