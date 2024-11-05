import os
import openai
from dotenv import load_dotenv
import chainlit as cl
from src.global_settings import CONVERSATION_FILE
from src.chat_engine import initialize_chatbot, load_chat_store, save_chat_store

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# OpenAI client settings
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
    # Load or initialize the chat store (conversation memory)
    chat_store = load_chat_store(CONVERSATION_FILE)
    agent = initialize_chatbot(chat_store)

    # Get the user query from Chainlit message
    user_query = message.content

    # Chainlit message object to stream tokens
    msg = cl.Message(content="")

    # Prepare messages history
    message_history = [{"role": "system", "content": "You are a helpful assistant."}]
    message_history.append({"role": "user", "content": user_query})

    # Streaming the response from OpenAI
    try:
        stream = await openai.ChatCompletion.acreate(
            model=settings["model"],
            messages=message_history,
            stream=True,
            **settings
        )

        async for part in stream:
            if token := part['choices'][0]['delta'].get('content', ''):
                await msg.stream_token(token)

        message_history.append({"role": "assistant", "content": msg.content})
        await msg.update()

        # Save chat store (conversation memory)
        save_chat_store(CONVERSATION_FILE, chat_store)
        print("Message saved to disk")

    except Exception as e:
        print(f"Error during streaming: {e}")
