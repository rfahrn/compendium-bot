# Tools_agent/tavily_tool.py

from tavily import TavilyClient
import os
import streamlit as st
tavily_api_key = st.secrets["tavily"]["TAVILY_API_KEY"]
client = TavilyClient(api_key=tavily_api_key)

def smart_tavily_answer(query):
    """Use Tavily to fetch and summarize web results."""
    results = client.search(query=query, search_depth="advanced", include_answer=True)
    
    answer = results.get("answer")
    urls = [r["url"] for r in results.get("results", [])]

    if not answer:
        return f"⚠️ Keine Antwort gefunden.\n\n🔗 Links:\n" + "\n".join(f"- {url}" for url in urls[:3])
    
    return f"**Antwort:** {answer}\n\n🔗 Links:\n" + "\n".join(f"- {url}" for url in urls[:3])
