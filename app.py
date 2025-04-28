# app.py

import os
import streamlit as st
from dotenv import load_dotenv

from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool

# Import your tools
from Tools_agent.compendium_tool import get_compendium_info
from Tools_agent.faiss_tool import search_faiss
from Tools_agent.openfda_tool import search_openfda
from Tools_agent.tavily_tool import smart_tavily_answer
from Tools_agent.alerts_tool import search_medication_alerts

# === Load environment
load_dotenv()

# === Streamlit Page Setup
st.set_page_config(page_title="💊 Medizinischer Assistent", layout="centered")

st.markdown("""
<style>
    .main-header { font-size: 2.5rem; margin-bottom: 1.5rem; }
    .subheader { font-size: 1.5rem; margin-top: 2rem; margin-bottom: 1rem; }
    .result-box { background-color: #f0f2f6; padding: 1.5rem; border-radius: 0.5rem; margin-top: 1rem; }
    .thought-box { background-color: #e8f0fe; padding: 1rem; border-radius: 0.5rem; margin-top: 1rem; }
</style>
""", unsafe_allow_html=True)

# === Header
st.markdown('<div class="main-header">💊 Medizinischer Assistent</div>', unsafe_allow_html=True)
st.write("Dieser Assistent kann medizinische Informationen aus Compendium.ch, OpenFDA, lokalen Dokumenten (FAISS) und dem Web sammeln.")

# === Setup Tools
tools = [
    Tool(name="CompendiumTool", func=get_compendium_info, description="Hole offizielle Medikamenteninfos von Compendium.ch"),
    Tool(name="FAISSRetrieverTool", func=search_faiss, description="Durchsuche lokale medizinische FAISS-Datenbank"),
    Tool(name="OpenFDATool", func=search_openfda, description="Hole vollständige Informationen aus OpenFDA-Datenbank"),
    Tool(name="TavilySearchTool", func=smart_tavily_answer, description="Suche im Web nach aktuellen Infos oder News"),
    Tool(name="MedicationAlertsTool", func=search_medication_alerts, description="Suche aktuelle Warnungen oder Sicherheitshinweise"),
]

# === Setup LLM
open_ai_key = st.secrets["openai"]["OPENAI_KEY"]
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.2,
    streaming=True,
    openai_api_key=open_ai_key,
)

# === Setup Agent
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
            "Lies die vollständigen Antworten der Tools. "
            "Extrahiere nur die relevanten Infos für die gestellte Frage. "
            "Antworte klar, präzise und auf Deutsch."
        ),
        "return_intermediate_steps": True,
        "max_iterations": 4,
    }
)

# === Frage-Typen und Optionen
question_types = {
    "💊 Wirkung": "Was ist die Wirkung von",
    "🩺 Nebenwirkungen": "Welche Nebenwirkungen hat",
    "🤰 Schwangerschaft und Stillzeit": "Ist sicher in der Schwangerschaft und Stillzeit von",
    "⚠️ Warnungen": "Welche Warnungen gibt es für",
    "💉 Anwendung": "Wie wird",
    "🧪 Inhaltsstoffe": "Welche Inhaltsstoffe (aktive und inaktive) sind in",
    "📦 Lagerung": "Wie sollte man lagern",
    "⚡ Interaktionen": "Welche Interaktionen gibt es bei",
    "📏 Dosierung": "Wie lautet die empfohlene Dosierung von",
    "🔍 Wirkstoffe": "Welche Wirkstoffe enthält",
    "🌡️ Haltbarkeit ohne Kühlung": "Wie lange ist haltbar ohne Kühlung",
    "🌍 Internationale Interaktionen": "Gibt es bekannte Interaktionen mit internationalen Medikamenten für",
}

input_type_options = {
    "🧪 Wirkstoff": "Wirkstoff",
    "💊 Medikament": "Medikament"
}

# === Streamlit Inputs
st.markdown('<div class="subheader">🔎 Frage stellen</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    question_type = st.selectbox("Fragetyp auswählen:", list(question_types.keys()))
with col2:
    input_type = st.selectbox("Art der Eingabe:", list(input_type_options.keys()))

medication_name = st.text_input("Name des Medikaments oder Wirkstoffs", placeholder="z.B. Dafalgan, Anthim, etc.")

run_button = st.button("🚀 Anfrage starten")

# === Main Logic
if run_button and medication_name:
    query_prefix = question_types[question_type]
    input_type_str = input_type_options[input_type]
    full_prompt = f"{query_prefix} {medication_name}? ({input_type_str})"

    st.markdown('<div class="subheader">🧠 Frage-Formulierung</div>', unsafe_allow_html=True)
    st.write(f"**🧠 Frage:** {full_prompt}")

    with st.spinner('🔎 Suche läuft...'):
        try:
            result = agent.invoke({"input": full_prompt})   # <<<<<<--- CORRECT CALL
            final_answer = result["output"]
            intermediate_steps = result.get("intermediate_steps", [])
        except Exception as e:
            st.error(f"❌ Fehler beim Ausführen des Assistenten: {e}")
            final_answer = None
            intermediate_steps = None

    # === Show Thinking Steps
    for idx, step in enumerate(intermediate_steps):
        thought = step[0].log
        action = step[1].tool
        action_input = step[1].tool_input
        st.markdown(f'''
        <div class="thought-box">
            <b>🧠 Gedanke {idx+1}:</b> {thought}<br>
            <b>🔧 Aktion:</b> {action}<br>
            <b>📥 Eingabe:</b> {action_input}
        </div>
        ''', unsafe_allow_html=True)

    # === Show Final Answer
    if final_answer:
        st.markdown('<div class="subheader">📋 Endgültige Antwort</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box">{final_answer}</div>', unsafe_allow_html=True)

elif run_button:
    st.warning("⚠️ Bitte gib den Namen eines Medikaments oder Wirkstoffs ein.")

