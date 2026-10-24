import os

from openai import OpenAI

client = OpenAI(
    base_url=os.environ["ASI1_BASE_URL"],
    api_key=os.environ["ASI1_API_KEY"],
)


def ask_asi1(messages: list) -> str:
    """Send a chat completion request to the ASI:One model and return the reply text."""
    completion = client.chat.completions.create(
        model="asi1",
        messages=messages,
        max_tokens=4096,
    )
    return completion.choices[0].message.content or ""
