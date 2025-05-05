# -*- coding: utf-8 -*-
import os
import streamlit as st
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.agents import AgentExecutor
from langchain.tools import Tool
from Tools_agent.compendium_tool import get_compendium_info
from Tools_agent.faiss_tool import search_faiss
from Tools_agent.openfda_tool import search_openfda
from Tools_agent.tavily_tool import smart_tavily_answer
from Tools_agent.alerts_tool import search_medication_alerts
from langchain.callbacks.streamlit import (
    StreamlitCallbackHandler,
)
import streamlit as st

load_dotenv()

st.set_page_config(page_title="💊 Medizinischer Assistent", layout="centered")

st.markdown("""
<style>
    .main-header { font-size: 2.5rem; margin-bottom: 1.5rem; }
    .subheader { font-size: 1.5rem; margin-top: 2rem; margin-bottom: 1rem; }
    .result-box { background-color: #f0f2f6; padding: 1.5rem; border-radius: 0.5rem; margin-top: 1rem; }
    .thought-box { background-color: #e8f0fe; padding: 1rem; border-radius: 0.5rem; margin-top: 1rem; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">💊 Medizinischer Assistent</div>', unsafe_allow_html=True)
st.write("Dieser Assistent nutzt Compendium.ch, OpenFDA, lokale FAISS-Datenbanken und Websuche für medizinische Informationen.")

tools = [
    Tool(name="CompendiumTool", func=get_compendium_info, description="Hole offizielle Medikamenteninfos von Compendium.ch"),
    Tool(name="FAISSRetrieverTool", func=search_faiss, description="Durchsuche lokale medizinische FAISS-Datenbank"),
    Tool(name="OpenFDATool", func=search_openfda, description="Hole vollständige Informationen aus OpenFDA-Datenbank"),
    Tool(name="TavilySearchTool", func=smart_tavily_answer, description="Suche aktuelle Infos im Web"),
    Tool(name="MedicationAlertsTool", func=search_medication_alerts, description="Suche Medikamentenwarnungen"),
]

openai_key = st.secrets["openai"]["OPENAI_KEY"]
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.2,
    streaming=True,
    openai_api_key=openai_key,
)

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True,
    agent_kwargs={
        "system_message": (
            "Du bist ein klinischer Assistent. "
            "Du darfst Tools verwenden. "
            "Lies sorgfältig Antworten. "
            "Fokussiere auf relevante Informationen. "
            "Antworte auf Deutsch und präzise."
        ),
        "return_intermediate_steps": True,
        "max_iterations": 5,
    }
)

question_types = {
    "💊 Wirkung": "Was ist die Wirkung von",
    "🩺 Nebenwirkungen": "Welche Nebenwirkungen hat",
    "🤰 Schwangerschaft und Stillzeit": "Ist sicher in der Schwangerschaft und Stillzeit von",
    "⚠️ Warnungen": "Welche Warnungen gibt es für",
    "💉 Anwendung": "Wie wird",
    "🧪 Inhaltsstoffe": "Welche Inhaltsstoffe sind in",
    "📦 Lagerung": "Wie sollte man lagern",
    "⚡ Interaktionen": "Welche Interaktionen gibt es bei",
    "📏 Dosierung": "Wie lautet die empfohlene Dosierung von",
    "🔍 Wirkstoffe": "Welche Wirkstoffe enthält",
    "🌡️ Haltbarkeit": "Wie lange ist haltbar ohne Kühlung",
    "🌍 Internationale Interaktionen": "Gibt es Interaktionen mit internationalen Medikamenten für",
}

input_type_options = {
    "🧪 Wirkstoff": "Wirkstoff",
    "💊 Medikament": "Medikament"
}


st.markdown('<div class="subheader">🔎 Anfrage stellen</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    question_type = st.selectbox("Fragetyp auswählen:", list(question_types.keys()))
with col2:
    input_type = st.selectbox("Art der Eingabe:", list(input_type_options.keys()))

medication_name = st.text_input("Name des Medikaments oder Wirkstoffs", placeholder="z.B. Dafalgan, Anthim, etc.")
run_button = st.button("🚀 Anfrage starten")
st_callback = StreamlitCallbackHandler(st.container())

import re
# URL extractor
def extract_urls(text):
    url_pattern = r"(https?://\S+)"
    return re.findall(url_pattern, text)

if run_button and medication_name:
    query_prefix = question_types[question_type]
    input_type_str = input_type_options[input_type]
    full_prompt = f"{query_prefix} {medication_name}? ({input_type_str})"

    st.markdown('<div class="subheader">🧠 Frage-Formulierung</div>', unsafe_allow_html=True)
    st.info(f"**🧠 Frage:** {full_prompt}")

    with st.status("🔍 Agent denkt...", expanded=True) as status:
        try:
            result = agent.invoke({"input": full_prompt}, callbacks=[st_callback], return_only_outputs=False)
            final_answer = result["output"]
            intermediate_steps = result.get("intermediate_steps", [])
            
            for idx, step in enumerate(intermediate_steps):
                with st.chat_message("assistant"):
                    st.markdown(f"🧠 **Gedanke {idx+1}:** {step[0].log}")
                    st.markdown(f"🔧 **Aktion:** {step[1].tool}")
                    st.markdown(f"📥 **Eingabe:** {step[1].tool_input}")

            status.update(label="✅ Denken abgeschlossen", state="complete")
        
        except Exception as e:
            st.error(f"❌ Fehler: {e}")
            status.update(label="❌ Fehler aufgetreten", state="error")
            final_answer = None

    if final_answer:
        st.markdown('<div class="subheader">📋 Endgültige Antwort</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box">{final_answer}</div>', unsafe_allow_html=True)
        urls_in_answer = extract_urls(final_answer)
        for url in urls_in_answer:
            st.markdown(f"🔗 **Gefundener Link in Antwort:** [{url}]({url})")
            
    if intermediate_steps:
        st.markdown('<div class="subheader">🧰 Verwendete Tools & Schritte</div>', unsafe_allow_html=True)
        for idx, step in enumerate(intermediate_steps):
            thought = step[0].log
            tool = step[1].tool
            tool_input = step[1].tool_input
            tool_output = step[1].tool_response

            st.markdown(f'<div class="thought-box">🧠 <b>Gedanke {idx+1}</b>: {thought}<br>'
                        f'🔧 <b>Tool</b>: {tool}<br>'
                        f'📥 <b>Eingabe</b>: {tool_input}<br>'
                        f'📤 <b>Antwort</b>: {tool_output}</div>', unsafe_allow_html=True)

            # Optional: extract and highlight URLs
            if isinstance(tool_output, str) and "http" in tool_output:
                urls = [word for word in tool_output.split() if word.startswith("http")]
                for url in urls:
                    st.markdown(f"🔗 **Gefundener Link:** [{url}]({url})")

elif run_button:
    st.warning("⚠️ Bitte gib den Namen eines Medikaments oder Wirkstoffs ein.")
