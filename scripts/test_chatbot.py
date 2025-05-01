#test_chatbot.py
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from src.llm_setup import get_chat_engine
from src.prompts import test_prompts

async def test_chatbot():
    chat_engine = get_chat_engine()
    for prompt in test_prompts[:5]:  # Test first 5 prompts
        print(f"Prompt: {prompt}")
        response = await chat_engine.chat(prompt)
        print(f"Response: {response}\n")

if __name__ == "__main__":
    asyncio.run(test_chatbot())