import os
import openai
import fitz  # PyMuPDF for reading PDFs
from pathlib import Path
from llama_index.core import VectorStoreIndex, StorageContext, Document
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.llms.openai import OpenAI
from llama_index.core.query_engine import SubQuestionQueryEngine
from llama_index.agent.openai import OpenAIAgent
from llama_index.core import load_index_from_storage
import chainlit as cl

# Import chat store and memory buffer
from llama_index.core.storage.chat_store import SimpleChatStore
from llama_index.core.memory import ChatMemoryBuffer

os.environ["OPENAI_API_KEY"] = "sk-j0X3snByBRXjyJXKG_urCfefY2ANGbKzexJWCaTg2bT3BlbkFJaHBWZOUCk3lWTaxHhVOsHgU5V99JkPPn9a3Yk2Qv0A"
openai.api_key = os.environ["OPENAI_API_KEY"]

# Function to read PDFs and convert them to Document objects
def read_pdf(file_path):
    documents = []
    with fitz.open(file_path) as pdf:
        text = ""
        for page_num in range(pdf.page_count):
            page = pdf[page_num]
            text += page.get_text()
        documents.append(Document(text=text))
    return documents

# Function to load all documents from the specified directory
def load_documents_from_folder(folder_path):
    documents = []
    for file_name in os.listdir(folder_path):
        file_path = Path(folder_path) / file_name
        if file_path.suffix == '.pdf':
            documents.extend(read_pdf(file_path))
    return documents

# Set the data folder path
data_folder_path = "C:/Users/nguye/OneDrive/Documents/GitHub/ChatbotAI/MyChatBot/data"  # Update this path as necessary
documents = load_documents_from_folder(data_folder_path)

# Create a storage context and index the documents
storage_context = StorageContext.from_defaults()
index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
storage_context.persist(persist_dir="./storage/index")

# Load the index
storage_context = StorageContext.from_defaults(persist_dir="./storage/index")
index = load_index_from_storage(storage_context)

# Create a query engine tool
query_engine_tool = QueryEngineTool(
    query_engine=index.as_query_engine(),
    metadata=ToolMetadata(name="index", description="Index for various document types")
)

# Setup the query engine
query_engine = SubQuestionQueryEngine.from_defaults(
    query_engine_tools=[query_engine_tool],
    llm=OpenAI(model="gpt-4o-mini")
)

tools = [query_engine_tool]

# Load or initialize chat store
persist_path = "C:/Users/nguye/OneDrive/Documents/GitHub/ChatbotAI/MyChatBot/chat_store.json"
if os.path.exists(persist_path):
    chat_store = SimpleChatStore.from_persist_path(persist_path)
else:
    chat_store = SimpleChatStore()

chat_memory = ChatMemoryBuffer.from_defaults(
    token_limit = 3000,
    chat_store = chat_store,
    chat_store_key = "user1",
)

# Initialize the chatbot agent with memory
agent = OpenAIAgent.from_tools(tools, memory=chat_memory, verbose=True)

@cl.on_chat_start
async def chat_start():
    await cl.Message(content="Welcome! Ask me anything about Vietnamese meals you want to cook").send()

@cl.on_message
async def main(message: cl.Message):
    content = message.content
    response = agent.chat(content)
    
    # Print the response to the chat
    await cl.Message(content=str(response)).send()


    # Save chat history after each message
    try:
        chat_store.persist(persist_path=persist_path)
        print("Chat history saved to disk")
    except Exception as e:
        print(f"Error saving chat history: {e}")
    

# Save chat history on shutdown
import atexit

@atexit.register
def save_chat_history():
    chat_store.persist(persist_path=persist_path)
    print("Chat history saved to disk")