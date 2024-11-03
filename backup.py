import os
import openai
import fitz  # PyMuPDF for reading PDFs
from pathlib import Path
from llama_index.core import VectorStoreIndex, StorageContext, Document
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.llms.openai import OpenAI
from llama_index.core.query_engine import SubQuestionQueryEngine
from llama_index.agent.openai import OpenAIAgent
from llama_index.core import load_index_from_storage  # Add this import
import chainlit as cl

os.environ["OPENAI_API_KEY"] = "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"
openai.api_key = os.environ["OPENAI_API_KEY"]

# Function to read PDFs and convert them to Document objects
def read_pdf(file_path):
    documents = []
    with fitz.open(file_path) as pdf:
        text = ""
        for page_num in range(pdf.page_count):
            page = pdf[page_num]
            text += page.get_text()
        # Create a Document object with the complete text
        documents.append(Document(text=text))
    return documents



# Function to load all documents from the specified directory
def load_documents_from_folder(folder_path):
    documents = []
    for file_name in os.listdir(folder_path):
        file_path = Path(folder_path) / file_name
        if file_path.suffix == '.pdf':
            documents.extend(read_pdf(file_path))
        # Add more conditions here if you want to handle other file types (e.g., .txt, .docx)
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

# Initialize the chatbot agent
agent = OpenAIAgent.from_tools(tools, verbose=True)

@cl.on_chat_start
async def chat_start():
    await cl.Message(content="Welcome! Ask me anything about Vietnamese meals you want to cook").send()

@cl.on_message
async def main(message: cl.Message):
    content = message.content
    response = agent.chat(content)
    await cl.Message(content=str(response)).send()