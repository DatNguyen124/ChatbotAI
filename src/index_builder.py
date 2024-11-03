# index_builder.py

from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage
from src.global_settings import INDEX_STORAGE

def create_index(documents, storage_context):
    index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
    storage_context.persist(persist_dir=INDEX_STORAGE)
    return index

def load_index(storage_context):
    index = load_index_from_storage(storage_context)
    return index

