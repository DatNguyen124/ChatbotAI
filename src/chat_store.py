import os
import json
from llama_index.core.storage.chat_store import SimpleChatStore
from llama_index.core.memory import ChatMemoryBuffer

def load_chat_store(persist_path):
    if os.path.exists(persist_path):
        try:
            with open(persist_path, 'r') as file:
                if os.path.getsize(persist_path) > 0:  # Check if the file is not empty
                    chat_store = SimpleChatStore.from_persist_path(persist_path)
                else:
                    chat_store = SimpleChatStore()
        except json.JSONDecodeError:
            chat_store = SimpleChatStore()  # Handle invalid JSON
    else:
        chat_store = SimpleChatStore()
    return chat_store

def save_chat_store(persist_path, chat_store):
    chat_store.persist(persist_path=persist_path)