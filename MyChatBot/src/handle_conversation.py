# FILE: src/handle_conversation.py
import openai
from src.chat_store import load_chat_store
from src.index_builder import create_index, load_index
from src.ingest_pipeline import load_documents_from_folder
from src.global_settings import CONVERSATION_FILE, STORAGE_PATH
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.agent.openai import OpenAIAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.query_engine import SubQuestionQueryEngine
from llama_index.core import StorageContext



def display_messages(messages):
    for message in messages:
        print(f"{message['timestamp']}: {message['sender']}: {message['text']}")

def initialize_chatbot(api_key, data_folder_path = STORAGE_PATH, persist_path = CONVERSATION_FILE, model="gpt-4o-mini", token_limit=3000, chat_store_key="user1"):
    
    openai.api_key = api_key
    
    # Load all documents from the specified directory
    documents = load_documents_from_folder(data_folder_path)
    
    # Create a storage context and index the documents
    storage_context = StorageContext.from_defaults()
    index = create_index(documents, storage_context)
    
    # Load the index
    storage_context = StorageContext.from_defaults(persist_dir="./storage/index")
    index = load_index(storage_context)
    
    # Create a query engine tool
    query_engine_tool = QueryEngineTool(
        query_engine=index.as_query_engine(),
        metadata=ToolMetadata(name="index", description="Index for various document types")
    )
    
    # Setup the query engine
    query_engine = SubQuestionQueryEngine.from_defaults(
        query_engine_tools=[query_engine_tool],
        llm=OpenAI(model=model)
    )
    
    tools = [query_engine_tool]
    
    # Load or initialize chat store
    chat_store = load_chat_store(persist_path)
    
    # Initialize chat memory
    chat_memory = ChatMemoryBuffer.from_defaults(
        token_limit=token_limit,
        chat_store=chat_store,
        chat_store_key=chat_store_key,
    )
    
    # Initialize the chatbot agent with memory
    agent = OpenAIAgent.from_tools(tools, memory=chat_memory, verbose=True)
    
    return agent
