import os
import openai
from dotenv import load_dotenv
import chainlit as cl
import atexit

from src.global_settings import CONVERSATION_FILE
from src.chat_store import save_chat_store
from src.handle_conversation import initialize_chatbot

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from the environment variable
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize chatbot with memory and query engine
chatbot = initialize_chatbot(openai_api_key)


@cl.on_chat_start
async def chat_start():
    await cl.Message("Welcome! Ask me anything about Vietnamese meals you want to cook").send()

@cl.on_message
async def main(message: cl.Message):
    
    content = message.content
    response = chatbot.chat(content)
    
    # Send the response back to the user
    await cl.Message(content=str(response)).send()

    # Save chat history after each message
    try:
        save_chat_store(CONVERSATION_FILE, chatbot.memory.chat_store)
        print("Chat history saved to disk")
    except Exception as e:
        print(f"Error saving chat history: {e}")
