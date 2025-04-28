# Tools_agent/faiss_tool.py

import faiss
import os
import pickle
import numpy as np
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
import PyMuPDF  as fitz # PyMuPDF for PDFs

# Tools_agent/faiss_tool.py

import faiss
import os
import pickle
import numpy as np
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
import fitz  # PyMuPDF for PDFs
import streamlit as st

FAISS_FOLDER = "data/faiss_index"
openai_api_key = st.secrets["openai"]["OPENAI_KEY"]
embedding_model = OpenAIEmbeddings(openai_api_key=openai_api_key)

def load_faiss_index():
    try:
        return FAISS.load_local(FAISS_FOLDER, embeddings=embedding_model, allow_dangerous_deserialization=True)
    except Exception:
        return None

def search_faiss(query):
    vs = load_faiss_index()
    if not vs:
        return "❗ Kein FAISS Index verfügbar."
    retriever = vs.as_retriever(search_kwargs={"k": 3})
    docs = retriever.get_relevant_documents(query)
    return "\n\n".join(d.page_content for d in docs)

def upload_pdf_to_faiss(uploaded_file):
    """Extract text from PDF, split, embed, store FAISS"""
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = "\n".join(page.get_text() for page in doc)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    documents = text_splitter.create_documents([text])

    vs = FAISS.from_documents(documents, embedding_model)
    vs.save_local(FAISS_FOLDER)
    return "✅ PDF verarbeitet und FAISS Index aktualisiert!"
