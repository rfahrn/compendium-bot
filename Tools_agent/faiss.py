# faiss_tool.py

import faiss
from langchain_community.vectorstores import FAISS
import pickle
import numpy as np
import openai
import os
from langchain.tools import Tool
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain.tools.retriever import create_retriever_tool

load_dotenv()
openai.api_key = os.getenv('OPENAI_KEY')
FAISS_INDEX_PATH = "faiss_index/"
embedding_function = OpenAIEmbeddings(openai_api_key=openai.api_key)

vectorstore = FAISS.load_local(FAISS_INDEX_PATH, embeddings=embedding_function, allow_dangerous_deserialization=True )
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

def search_faiss(query):
    """Simple FAISS search function for agents."""
    docs = retriever.get_relevant_documents(query)
    if docs:
        return "\n\n".join(doc.page_content for doc in docs)
    else:
        return "Keine relevanten Informationen in der FAISS-Datenbank gefunden."


faiss_retriever_tool = Tool(
    name="FAISSRetriever",
    func=search_faiss,
    description="Suche relevante medizinische Informationen aus der lokalen Vektordatenbank (FAISS)."
)