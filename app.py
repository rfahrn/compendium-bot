# app.py
import os
import streamlit as st
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.agents import AgentExecutor
from langchain.agents import AgentOutputParser
from langchain.tools import Tool

# Import your tools
from Tools_agent.compendium_tool import get_compendium_info
from Tools_agent.faiss_tool import search_faiss
from Tools_agent.openfda_tool import search_openfda
from Tools_agent.tavily_tool import smart_tavily_answer
from Tools_agent.alerts_tool import search_medication_alerts
from langchain.callbacks import StreamlitCallbackHandler
# --- Load environment
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.agents import AgentType, initialize_agent
from langchain.agents.format_scratchpad import format_log_to_str
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.agents import AgentFinish
from langchain_core.output_parsers import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain.agents import create_react_agent  # <== use this

load_dotenv()

# --- Streamlit Setup
st.set_page_config(page_title="💊 Medizinischer Assistent", layout="centered")

st.markdown("""
<style>
    .main-header { font-size: 2.5rem; margin-bottom: 1.5rem; }
    .subheader { font-size: 1.5rem; margin-top: 2rem; margin-bottom: 1rem; }
    .result-box { background-color: #f0f2f6; padding: 1.5rem; border-radius: 0.5rem; margin-top: 1rem; }
    .thought-box { background-color: #e8f0fe; padding: 1rem; border-radius: 0.5rem; margin-top: 1rem; }
</style>
""", unsafe_allow_html=True)

# --- Page Header
st.markdown('<div class="main-header">💊 Medizinischer Assistent</div>', unsafe_allow_html=True)
st.write("Dieser Assistent nutzt Compendium.ch, OpenFDA, lokale FAISS-Datenbanken und Websuche für medizinische Informationen.")

# --- Setup Tools
tools = [
    Tool(name="CompendiumTool", func=get_compendium_info, description="Hole offizielle Medikamenteninfos von Compendium.ch"),
    Tool(name="FAISSRetrieverTool", func=search_faiss, description="Durchsuche lokale medizinische FAISS-Datenbank"),
    Tool(name="OpenFDATool", func=search_openfda, description="Hole vollständige Informationen aus OpenFDA-Datenbank"),
    Tool(name="TavilySearchTool", func=smart_tavily_answer, description="Suche aktuelle Infos im Web"),
    Tool(name="MedicationAlertsTool", func=search_medication_alerts, description="Suche Medikamentenwarnungen"),
]

# --- Setup LLM and Agent
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
        )
    }
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

# --- UI Form
st.markdown('<div class="subheader">🔎 Anfrage stellen</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    question_type = st.selectbox("Fragetyp auswählen:", list(question_types.keys()))
with col2:
    input_type = st.selectbox("Art der Eingabe:", list(input_type_options.keys()))

medication_name = st.text_input("Name des Medikaments oder Wirkstoffs", placeholder="z.B. Dafalgan, Anthim, etc.")
run_button = st.button("🚀 Anfrage starten")# --- Setup agent_executor properly
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    verbose=True,
    return_intermediate_steps=True,
    handle_parsing_errors=True,
)

st_callback = StreamlitCallbackHandler(parent_container=st.container())

# --- On run_button click
if run_button and medication_name:
    query_prefix = question_types[question_type]
    input_type_str = input_type_options[input_type]
    full_prompt = f"{query_prefix} {medication_name}? ({input_type_str})"

    st.markdown('<div class="subheader">🧠 Frage-Formulierung</div>', unsafe_allow_html=True)
    st.info(f"**🧠 Frage:** {full_prompt}")

    with st.status("🔍 Agent denkt...", expanded=True) as status:
        try:
            result = agent_executor.invoke(
                {"input": full_prompt},
                callbacks=[st_callback]
            )
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

    # --- Show final answer
    if final_answer:
        st.markdown('<div class="subheader">📋 Endgültige Antwort</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-box">{final_answer}</div>', unsafe_allow_html=True)

elif run_button:
    st.warning("⚠️ Bitte gib den Namen eines Medikaments oder Wirkstoffs ein.")
