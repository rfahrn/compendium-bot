# app.py

import os
import time
import streamlit as st
from dotenv import load_dotenv
import asyncio

# LangChain Imports
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import Tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

# Your Tools
from Tools_agent.compendium_tool import get_compendium_info
from Tools_agent.faiss_tool import search_faiss
from Tools_agent.openfda_tool import search_openfda
from Tools_agent.tavily_tool import smart_tavily_answer
from Tools_agent.alerts_tool import search_medication_alerts

# --- Load environment
load_dotenv()

# --- Streamlit page config
st.set_page_config(page_title="💊 Medizinischer Assistent", layout="centered")

st.markdown("""
<style>
    .main-header { font-size: 2.5rem; margin-bottom: 1.5rem; }
    .subheader { font-size: 1.5rem; margin-top: 2rem; margin-bottom: 1rem; }
    .result-box { background-color: #f0f2f6; padding: 1.5rem; border-radius: 0.5rem; margin-top: 1rem; }
    .thought-box { background-color: #e8f0fe; padding: 1rem; border-radius: 0.5rem; margin-top: 1rem; }
</style>
""", unsafe_allow_html=True)

# --- Header
st.markdown('<div class="main-header">💊 Medizinischer Assistent</div>', unsafe_allow_html=True)
st.write("Dieser Assistent nutzt Compendium.ch, OpenFDA, lokale FAISS-Datenbanken und Websuche für medizinische Informationen.")

# --- Define tools
tools = [
    Tool(name="CompendiumTool", func=get_compendium_info, description="Hole Medikamenteninfos von Compendium.ch"),
    Tool(name="FAISSRetrieverTool", func=search_faiss, description="Suche in lokalen FAISS-Daten"),
    Tool(name="OpenFDATool", func=search_openfda, description="Hole Infos aus OpenFDA"),
    Tool(name="TavilySearchTool", func=smart_tavily_answer, description="Websuche nach aktuellen Informationen"),
    Tool(name="MedicationAlertsTool", func=search_medication_alerts, description="Suche Medikamentenwarnungen"),
]

# --- Setup LLM
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.2,
    streaming=True,
    openai_api_key=st.secrets["openai"]["OPENAI_KEY"],
)

# --- Setup custom prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "Du bist ein klinischer Assistent. Nutze wenn nötig folgende Tools:\n{tools}\n\nAntworte präzise auf Deutsch."),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# --- Create agent
agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=prompt,
)

# --- Create agent executor
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True
)

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

# --- Streamlit UI
st.markdown('<div class="subheader">🔎 Anfrage stellen</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    question_type = st.selectbox("Fragetyp auswählen:", list(question_types.keys()))
with col2:
    input_type = st.selectbox("Art der Eingabe:", list(input_type_options.keys()))

medication_name = st.text_input("Name des Medikaments oder Wirkstoffs", placeholder="z.B. Dafalgan, Anthim, etc.")
run_button = st.button("🚀 Anfrage starten")
# --- Async -> Sync Wrapper
async def agent_async_gen(full_prompt):
    async for chunk in agent_executor.astream({
        "input": full_prompt,
        "agent_scratchpad": []
    }):
        if "actions" in chunk:
            for action in chunk["actions"]:
                yield f"🔧 **Aktion:** `{action.tool}` mit Eingabe `{action.tool_input}`\n\n"
        if "steps" in chunk:
            for step in chunk["steps"]:
                yield f"📋 **Beobachtung:** `{step.observation}`\n\n"
        if "output" in chunk:
            yield f"\n### 📋 Endgültige Antwort:\n{chunk['output']}"

def agent_sync_gen(full_prompt):
    return asyncio.run(agent_async_gen(full_prompt))

# --- Main logic
if run_button and medication_name:
    query_prefix = question_types[question_type]
    input_type_str = input_type_options[input_type]
    full_prompt = f"{query_prefix} {medication_name}? ({input_type_str})"

    st.markdown('<div class="subheader">🧠 Frage-Formulierung</div>', unsafe_allow_html=True)
    st.info(f"**🧠 Frage:** {full_prompt}")

    with st.status("🔎 Assistent arbeitet...", expanded=True):
        st.write_stream(agent_sync_gen(full_prompt))

elif run_button:
    st.warning("⚠️ Bitte gib den Namen eines Medikaments oder Wirkstoffs ein.")