# Tools_agent/alerts_tool.py
# Tools_agent/alerts_tool.py

import os
from tavily import TavilyClient

# Setup Tavily client
import streamlit as st

tavily_api_key = st.secrets["tavily"]["TAVILY_API_KEY"]
client = TavilyClient(api_key=tavily_api_key)

def search_medication_alerts(query: str) -> str:
    """Search for medication alerts, recalls, or safety warnings."""

    search_query = f"{query} Medikament Warnung Rückruf Sicherheit site:fda.gov OR site:ema.europa.eu OR site:pharmazeutische-zeitung.de"

    try:
        results = client.search(query=search_query, search_depth="advanced", include_answer=True)

        answer = results.get("answer")
        urls = [r["url"] for r in results.get("results", [])]

        if answer:
            response = f"⚠️ **Gefundene Warnungen/Sicherheitsinfos zu '{query}':**\n\n{answer}\n\n🔗 Quellen:\n"
            response += "\n".join(f"- {url}" for url in urls[:5])
            return response
        else:
            # If no answer but links exist, still show them
            if urls:
                return (
                    f"⚠️ **Keine klare Antwort, aber mögliche relevante Quellen für '{query}':**\n\n" +
                    "\n".join(f"- {url}" for url in urls[:5])
                )
            else:
                return f"✅ Keine bekannten Warnungen oder Rückrufe für '{query}' gefunden."

    except Exception as e:
        print(f"❗ Fehler bei der Tavily-Alertsuche: {e}")
        return "❗ Fehler beim Abrufen von Sicherheitsinformationen."
