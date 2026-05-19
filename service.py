import os
import asyncio
from collections import defaultdict
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """
You are an expert AI assistant.

Rules:
- Answer in Uzbek
- Be concise but deep
- Explain technical topics at expert level
"""

MAX_OUTPUT_TOKENS = 800
MAX_HISTORY_MESSAGES = 20

TEMPERATURE = 0.5
TOP_P = 0.95


class ChatMemory:
    def __init__(self):
        self.messages = []

    def add_user(self, text: str):
        self.messages.append({
            "role": "user",
            "content": text
        })

    def add_assistant(self, text: str):
        self.messages.append({
            "role": "assistant",
            "content": text
        })

    def get_context(self):
        return self.messages[-MAX_HISTORY_MESSAGES:]

    def clear(self):
        self.messages = []


user_memories = defaultdict(ChatMemory)


async def chatbot(user_id: str, prompt: str):
    memory = user_memories[user_id]

    memory.add_user(prompt)

    input_messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        *memory.get_context()
    ]

    assistant_response = ""

    async with client.responses.stream(
            model=MODEL,
            input=input_messages,
            max_output_tokens=MAX_OUTPUT_TOKENS,
            temperature=TEMPERATURE,
            top_p=TOP_P,
    ) as stream:

        async for event in stream:
            if event.type == "response.output_text.delta":
                chunk = event.delta
                assistant_response += chunk
                yield chunk
                await asyncio.sleep(0)
    memory.add_assistant(assistant_response)


def clear_user_memory(user_id: str):
    if user_id in user_memories:
        user_memories[user_id].clear()


def get_user_history(user_id: str):
    return user_memories[user_id].messages
