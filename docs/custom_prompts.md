# Custom Prompts for LLMSecretDetector

Custom prompts are a powerful feature of the `LLMSecretDetector` that allow users to tailor the detection process to their specific needs. By providing a custom prompt, you can guide the language model to focus on particular types of sensitive information and format the output in a desired way.

## Purpose of Custom Prompts

Custom prompts enhance the detection process by:
- **Targeting Specific Information**: Directing the model to look for specific types of sensitive data, such as API keys, tokens, or credentials.
- **Formatting Output**: Instructing the model to return the detected information in a structured format, such as JSON.
- **Improving Accuracy**: Providing context and instructions that help the model understand what to look for, thereby improving detection accuracy.

## Creating Custom Prompts

When creating custom prompts, consider the following guidelines:
- **Be Specific**: Clearly specify what type of information you want the model to detect.
- **Provide Context**: Include any necessary context that might help the model understand the task.
- **Define Output Format**: If you need the output in a specific format, such as JSON, include this in the prompt.

### Example of a Custom Prompt

Here's an example of a custom prompt used to extract secrets from text:

```python
custom_prompt = (
    "Extract secrets from the following:\n\n"
    "Only include API keys, secrets, tokens, or credentials. Use the following output format as JSON: {{\"secrets\": [...]}}\n\n"
    "Text: {text}"
)
```

## Using Custom Prompts with LLMSecretDetector

To use a custom prompt with the `LLMSecretDetector`, pass it as the `prompt_format` parameter when initializing the detector.

### Example Usage

```python
from sentinel import LLMSecretDetector

# Define a custom prompt
custom_prompt = (
    "Extract secrets from the following:\n\n"
    "Only include API keys, secrets, tokens, or credentials. Use the following output format as JSON: {{\"secrets\": [...]}}\n\n"
    "Text: {text}"
)

# Initialize the detector with the custom prompt
detector = LLMSecretDetector(model, prompt_format=custom_prompt)

# Use the detector in your LLM pipeline
```

## Benefits of Custom Prompts

- **Flexibility**: Custom prompts provide flexibility in defining what constitutes sensitive information and how it should be detected.
- **Control**: Users have control over the detection process, allowing for tailored solutions that meet specific requirements.
- **Enhanced Detection**: By guiding the model with clear instructions, custom prompts can enhance the accuracy and reliability of the detection process.

Custom prompts are a valuable tool for users who need precise and reliable detection of sensitive information in their LLM interactions. By leveraging this feature, you can ensure that your detection process is both effective and aligned with your specific needs.