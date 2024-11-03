import os
import openai
from dotenv import load_dotenv
import chainlit as cl
import atexit

from src.global_settings import CONVERSATION_FILE
from src.chat_store import save_chat_store
from src.handle_conversation import initialize_chatbot

from openai import AsyncOpenAI

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from the environment variable
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize chatbot with memory and query engine
chatbot = initialize_chatbot(openai_api_key)
# Initialize AsyncOpenAI client
client = AsyncOpenAI(api_key=openai_api_key)

# Settings for the OpenAI model
settings = {
    "model": "gpt-3.5-turbo",
    "temperature": 0.7,
    "max_tokens": 500,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0,
}


@cl.on_chat_start
async def chat_start():
    await cl.Message("Welcome! Ask me anything about Vietnamese meals you want to cook").send()


@cl.on_message
async def main(message: cl.Message):
    # Retrieve message history from user session
    message_history = cl.user_session.get("message_history", [])
    message_history.append({"role": "user", "content": message.content})

    msg = cl.Message(content="")

    # Stream response from OpenAI API
    stream = await client.chat.completions.create(
        messages=message_history, stream=True, **settings
    )

    async for part in stream:
        if token := part.choices[0].delta.content or "":
            await msg.stream_token(token)

    # Append assistant's message to history
    message_history.append({"role": "assistant", "content": msg.content})
    await msg.update()

    # Save chat history after each message
    try:
        save_chat_store(CONVERSATION_FILE, chatbot.memory.chat_store)
        print("Chat history saved to disk")
    except Exception as e:
        print(f"Error saving chat history: {e}")