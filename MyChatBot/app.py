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


# # Create a storage context and index the documents
# storage_context = StorageContext.from_defaults()
# index = create_index(documents, storage_context)

# # Load the index
# storage_context = StorageContext.from_defaults(persist_dir="./storage/index")
# index = load_index(storage_context)

# Create a query engine tool
# query_engine_tool = QueryEngineTool(
#     query_engine=index.as_query_engine(),
#     metadata=ToolMetadata(name="index", description="Index for various document types")
# )

# # Setup the query engine
# query_engine = SubQuestionQueryEngine.from_defaults(
#     query_engine_tools=[query_engine_tool],
#     llm=OpenAI(model="gpt-4o-mini")
# )

# tools = [query_engine_tool]

# # Load or initialize chat store
# persist_path = "C:/Users/nguye/OneDrive/Documents/GitHub/ChatbotAI/MyChatBot/chat_store.json"
# chat_store = load_chat_store(persist_path)

# chat_memory = ChatMemoryBuffer.from_defaults(
#     token_limit=3000,
#     chat_store=chat_store,
#     chat_store_key="user1",
# )

# # Initialize the chatbot agent with memory
# agent = OpenAIAgent.from_tools(tools, memory=chat_memory, verbose=True)

# @cl.on_chat_start
# async def chat_start():
#     await cl.Message(content="Welcome! Ask me anything about Vietnamese meals you want to cook").send()

# @cl.on_message
# async def main(message: cl.Message):
#     content = message.content
#     response = agent.chat(content)
    
#     # Print the response to the chat
#     await cl.Message(content=str(response)).send()

#     # Save chat history after each message
#     try:
#         save_chat_store(chat_store, persist_path)
#         print("Chat history saved to disk")
#     except Exception as e:
#         print(f"Error saving chat history: {e}")

# # Save chat history on shutdown
# @atexit.register
# def save_chat_history():
#     save_chat_store(chat_store, persist_path)
#     print("Chat history saved to disk")