import os
import openai
from dotenv import load_dotenv
import chainlit as cl
from src.global_settings import CONVERSATION_FILE
from src.chat_engine import initialize_chatbot, load_chat_store, save_chat_store

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")


@cl.on_chat_start
async def chat_start():
    await cl.Message("Welcome to our CookBot! Here, you can explore the rich culinary worlds of Vietnam, Korea, and Japan. Whether you’re looking for authentic recipes, step-by-step cooking directions, or a description of traditional dishes, I’m here to help you bring these vibrant flavors into your kitchen. Let’s get cooking!").send()

@cl.on_message
async def main(message: cl.Message):
    # Load or initialize the chat store (conversation memory)
    chat_store = load_chat_store(CONVERSATION_FILE)

    agent = initialize_chatbot(chat_store)

    # Get the user query from Chainlit message
    user_query = message.content
    response = agent.chat(user_query)

    await cl.Message(content=str(response)).send()
    
    try:
        save_chat_store(CONVERSATION_FILE, chat_store)
        print("message saved to disk")
    except Exception as e:
        print(f"Error saving chat history: {e}")

    # Send the response back to Chainlit UI
    #await message.send(bot_response)