# ingest_pipeline.py

import os
from pathlib import Path
import fitz  # PyMuPDF for reading PDFs
from llama_index.core import Document

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