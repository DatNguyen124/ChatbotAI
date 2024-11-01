import os
import openai
import json
import fitz  # PyMuPDF for reading PDFs
from pathlib import Path
from llama_index.core import VectorStoreIndex, StorageContext, Document
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.llms.openai import OpenAI
from llama_index.core.query_engine import SubQuestionQueryEngine
from llama_index.agent.openai import OpenAIAgent
from llama_index.core import load_index_from_storage
import chainlit as cl

# Set your OpenAI API key
os.environ["OPENAI_API_KEY"] = "sk-j0X3snByBRXjyJXKG_urCfefY2ANGbKzexJWCaTg2bT3BlbkFJaHBWZOUCk3lWTaxHhVOsHgU5V99JkPPn9a3Yk2Qv0A"
openai.api_key = os.environ["OPENAI_API_KEY"]

# Memory management
memory = []

# Load memory from a JSON file
def load_memory(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    return []

# Save memory to a JSON file
def save_memory(file_path, memory):
    with open(file_path, 'w') as file:
        json.dump(memory, file)

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
        # You can handle other file types here if needed
    return documents

# Set the data folder path
data_folder_path = "C:/Users/nguye/OneDrive/Documents/GitHub/ChatbotAI/MyChatBot/data"
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
    metadata=ToolMetadata(name="general_index", description="Index for various document types")
)

# Setup the query engine
query_engine = SubQuestionQueryEngine.from_defaults(
    query_engine_tools=[query_engine_tool],
    llm=OpenAI(model="gpt-4o-mini")
)

# Initialize the chatbot agent
tools = [query_engine_tool]
agent = OpenAIAgent.from_tools(tools, verbose=True)

# Memory file path
memory_file_path = "memory.json"
memory = load_memory(memory_file_path)

@cl.on_chat_start
async def chat_start():
    await cl.Message(content="Welcome! Ask me anything about Vietnamese meals you want to cook.").send()

@cl.on_message
async def main(message: cl.Message):
    global memory

    # Extract the message content properly
    user_input = message.content  # Use the correct attribute

    # Store user input in memory
    memory.append({"user": user_input})

    # Generate response from the agent
    response = agent.chat(user_input)

    # Extract the text from the response object (adjust based on your agent's API)
    response_text = response.text if hasattr(response, 'text') else str(response)

    # Store the bot's response in memory
    memory.append({"bot": response_text})

    # Save updated memory to file
    save_memory(memory_file_path, memory)

    # Send the response back to the user
    await cl.Message(content=response_text).send()

# Optional: Cleanup old memories to manage memory size
def clean_up_memory(max_size=10):
    """Remove old memories if memory exceeds max size."""
    if len(memory) > max_size:
        memory = memory[-max_size:]  # Keep only the most recent memories
        save_memory(memory_file_path, memory)  # Save cleaned memory

# Call clean_up_memory after saving memory to manage size
