# app.py

import os
import asyncio
import streamlit as st
from dotenv import load_dotenv

from langchain_community.chat_models import ChatOpenAI
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler

from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import Tool

# --- Import your tools
from Tools_agent.compendium_tool import get_compendium_info
from Tools_agent.faiss_tool import search_faiss
from Tools_agent.openfda_tool import search_openfda
from Tools_agent.tavily_tool import smart_tavily_answer
from Tools_agent.alerts_tool import search_medication_alerts

# --- Load environment
load_dotenv()

# --- Streamlit Setup
st.set_page_config(page_title="💊 Medizinischer Assistent", layout="centered")

st.markdown("""
<style>
    .main-header { font-size: 2.5rem; margin-bottom: 1.5rem; }
    .subheader { font-size: 1.5rem; margin-top: 2rem; margin-bottom: 1rem; }
    .result-box { background-color: #f0f2f6; padding: 1.5rem; border-radius: 0.5rem; margin-top: 1rem; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">💊 Medizinischer Assistent</div>', unsafe_allow_html=True)
st.write("Dieser Assistent nutzt Compendium.ch, OpenFDA, lokale FAISS-Datenbanken und Websuche für medizinische Informationen.")

# --- Define Tools
tools = [
    Tool.from_function(
        name="CompendiumTool",
        description="Hole offizielle Medikamenteninfos von Compendium.ch",
        func=get_compendium_info,
    ),
    Tool.from_function(
        name="FAISSRetrieverTool",
        description="Durchsuche lokale medizinische FAISS-Datenbank",
        func=search_faiss,
    ),
    Tool.from_function(
        name="OpenFDATool",
        description="Hole vollständige Informationen aus OpenFDA-Datenbank",
        func=search_openfda,
    ),
    Tool.from_function(
        name="TavilySearchTool",
        description="Suche aktuelle Infos im Web",
        func=smart_tavily_answer,
    ),
    Tool.from_function(
        name="MedicationAlertsTool",
        description="Suche Medikamentenwarnungen",
        func=search_medication_alerts,
    ),
]

# --- Setup LLM
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.2,
    streaming=True,
    openai_api_key=st.secrets["openai"]["OPENAI_KEY"],
)

# --- Define Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "Du bist ein klinischer Assistent. Du darfst Tools verwenden. Antworte klar auf Deutsch."),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

# --- Setup Agent
agent = create_react_agent(llm, tools, prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
).with_config({"run_name": "Agent"})

# --- Frage Typen
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

# --- UI Inputs
st.markdown('<div class="subheader">🔎 Anfrage stellen</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    question_type = st.selectbox("Fragetyp auswählen:", list(question_types.keys()))
with col2:
    input_type = st.selectbox("Art der Eingabe:", list(input_type_options.keys()))

medication_name = st.text_input("Name des Medikaments oder Wirkstoffs", placeholder="z.B. Dafalgan, Anthim, etc.")
run_button = st.button("🚀 Anfrage starten")

# --- Main Logic
if run_button and medication_name:

    query_prefix = question_types[question_type]
    input_type_str = input_type_options[input_type]
    reformulated_question = f"{query_prefix} {medication_name}? ({input_type_str})"

    st.markdown('<div class="subheader">🧠 Frage-Formulierung</div>', unsafe_allow_html=True)
    st.info(f"**🧠 Reformulierte Frage:** {reformulated_question}")

    st.markdown('<div class="subheader">🧠 Agent denkt...</div>', unsafe_allow_html=True)

    thought_placeholder = st.container()
    final_answer_placeholder = st.empty()

    async def stream_agent():
        async for chunk in agent_executor.astream({"input": reformulated_question}):
            if "actions" in chunk:
                for action in chunk["actions"]:
                    thought_placeholder.markdown(f"🔧 **Aktion:** `{action.tool}` mit Eingabe `{action.tool_input}`")
            elif "steps" in chunk:
                for step in chunk["steps"]:
                    thought_placeholder.markdown(f"📥 **Beobachtung:** `{step.observation}`")
            elif "output" in chunk:
                final_answer_placeholder.success(f"📋 Antwort: {chunk['output']}")

    asyncio.run(stream_agent())

elif run_button:
    st.warning("⚠️ Bitte gib den Namen eines Medikaments oder Wirkstoffs ein.")

