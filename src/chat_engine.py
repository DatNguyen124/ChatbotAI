import os
import json
from llama_index.core import load_index_from_storage
from llama_index.core import StorageContext
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.agent.openai import OpenAIAgent
from llama_index.core.storage.chat_store import SimpleChatStore
from src.global_settings import INDEX_STORAGE, CONVERSATION_FILE
from src.prompts import CUSTOM_AGENT_SYSTEM_TEMPLATE
from llama_index.llms.openai import OpenAI

def load_chat_store(persist_path):
    if os.path.exists(persist_path) and os.path.getsize(persist_path) > 0:
        try:
            chat_store = SimpleChatStore.from_persist_path(persist_path)
        except json.JSONDecodeError:
            chat_store = SimpleChatStore()
    else:
        chat_store = SimpleChatStore()
    return chat_store

def save_chat_store(persist_path, chat_store):
    chat_store.persist(persist_path=persist_path)

def initialize_chatbot(chat_store):
    memory = ChatMemoryBuffer.from_defaults(
        token_limit=3000,
        chat_store=chat_store
    )
    index = load_index_from_storage(
        storage_context=StorageContext.from_defaults(persist_dir=INDEX_STORAGE),
        index_id="vector"
    )
    query_engine = index.as_query_engine(
        similarity_top_k=3,
    )

    query_tool= QueryEngineTool(
        query_engine= query_engine, 
        metadata=ToolMetadata(
            name="CookBot",
            description=(
                f"Ask me anything about Vietnamese, Korean, and Japanese cuisine!"
            ),
        )
    )

    agent = OpenAIAgent.from_tools(
        tools = [query_tool],
        llm =OpenAI(model="gpt-4o-mini"),
        memory=memory,
        system_prompt=CUSTOM_AGENT_SYSTEM_TEMPLATE)
    return agent

