# app.py

import os
import streamlit as st
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import Tool
from langchain.callbacks import StreamlitCallbackHandler
from langchain_core.prompts import SystemMessagePromptTemplate

# Your Tools
from Tools_agent.compendium_tool import get_compendium_info
from Tools_agent.faiss_tool import search_faiss
from Tools_agent.openfda_tool import search_openfda
from Tools_agent.tavily_tool import smart_tavily_answer
from Tools_agent.alerts_tool import search_medication_alerts

# Load .env
load_dotenv()

# --- Streamlit Page
st.set_page_config(page_title="💊 Medizinischer Assistent", layout="centered")
st.title("💊 Medizinischer Assistent")
st.write("Dieser Assistent kombiniert Compendium.ch, OpenFDA, lokale FAISS-Daten und Websuche.")

# --- Define Tools
tools = [
    Tool(name="CompendiumTool", func=get_compendium_info, description="Hole Medikamenteninformationen von Compendium.ch"),
    Tool(name="FAISSRetrieverTool", func=search_faiss, description="Durchsuche lokale FAISS-Datenbank"),
    Tool(name="OpenFDATool", func=search_openfda, description="Hole vollständige Daten von OpenFDA"),
    Tool(name="TavilySearchTool", func=smart_tavily_answer, description="Suche aktuelle Webinformationen"),
    Tool(name="MedicationAlertsTool", func=search_medication_alerts, description="Suche Medikamentenwarnungen"),
]

# --- Setup LLM
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.2,
    streaming=True,
    openai_api_key=st.secrets["openai"]["OPENAI_KEY"],
)

# --- Setup Custom ReAct Agent
prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        "Du bist ein klinischer Assistent. "
        "Verwende wenn möglich die Tools. "
        "Denke Schritt für Schritt. "
        "Antworte auf Deutsch und präzise."
    ),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    return_intermediate_steps=True,
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

# --- UI
st.header("🔎 Anfrage stellen")
col1, col2 = st.columns(2)

with col1:
    question_type = st.selectbox("Fragetyp auswählen:", list(question_types.keys()))
with col2:
    input_type = st.selectbox("Art der Eingabe:", list(input_type_options.keys()))

medication_name = st.text_input("Name des Medikaments oder Wirkstoffs", placeholder="z.B. Dafalgan, Anthim, etc.")
run_button = st.button("🚀 Anfrage starten")

# --- Execution
if run_button and medication_name:
    query_prefix = question_types[question_type]
    input_type_str = input_type_options[input_type]
    full_prompt = f"{query_prefix} {medication_name}? ({input_type_str})"

    st.subheader("🧠 Formulierte Frage")
    st.info(full_prompt)

    with st.spinner("🔎 Der Assistent denkt..."):
        st_callback = StreamlitCallbackHandler(st.container())
        try:
            result = agent_executor.invoke({"input": full_prompt}, callbacks=[st_callback])

            final_answer = result["output"]
            intermediate_steps = result.get("intermediate_steps", [])

            st.subheader("🧠 Zwischenschritte (Chain of Thought)")
            for idx, step in enumerate(intermediate_steps):
                thought = step[0].log
                action = step[1].tool
                tool_input = step[1].tool_input

                st.markdown(f"""
                <div style="background-color:#e8f0fe;padding:10px;border-radius:8px;margin-bottom:10px;">
                <b>🧠 Gedanke {idx+1}:</b> {thought}<br>
                <b>🔧 Aktion:</b> {action}<br>
                <b>📥 Eingabe:</b> {tool_input}
                </div>
                """, unsafe_allow_html=True)

            st.success("✅ Denken abgeschlossen!")

            st.subheader("📋 Endgültige Antwort")
            st.markdown(f'<div class="result-box">{final_answer}</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ Fehler beim Ausführen: {e}")

elif run_button:
    st.warning("⚠️ Bitte gib den Namen eines Medikaments oder Wirkstoffs ein.")
