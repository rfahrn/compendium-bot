import streamlit as st
import os
import aiofiles
import asyncio
from dotenv import load_dotenv
from history_questions import HistoryQuestions
from browser_use import BrowserConfig, Agent, Browser
from browser_use.browser.context import BrowserContextConfig
from langchain_openai import ChatOpenAI
import subprocess
import time

# Load environment variables
load_dotenv()

# Initialize Streamlit page with custom theme
st.set_page_config(
    page_title="💊 Compendium Bot", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Add some custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        margin-bottom: 1.5rem;
    }
    .subheader {
        font-size: 1.5rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .stTextInput > div > div > input {
        background-color: #f0f2f6;
    }
    .result-box {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Header with nice styling
st.markdown('<div class="main-header">💊 Compendium Bot</div>', unsafe_allow_html=True)

# Description with better formatting
st.markdown("""
Dieser Bot kann im Compendium nach Medikamenteninformationen suchen.
Stelle eine Frage zu einem Medikament, um zu beginnen.
""")

# Setup the browser
config = BrowserConfig(headless=True)
browser = Browser(config=config)

# Initialize HistoryQuestions service
history_service = HistoryQuestions()

# Create two columns for main layout
col1, col2 = st.columns([3, 1])

with col1:
    # Text input for the question with improved styling
    question = st.text_input(
        "Was möchtest du wissen?",
        placeholder="z. B. Wirkung von Dafalgan, Dosierung etc."
    )

with col2:
    # Add some spacing to align the button with the input field
    st.markdown("<br>", unsafe_allow_html=True)
    # Green run button
    run_button = st.button("🚀 Browser Agent starten", type="primary", key="run_agent")

# Store question in session and add to history
if question:
    history_service.add_question(question)
    st.write(f"Du hast gefragt: *{question}*")
    st.session_state.question = question

# Create tabs for history and results
tab1, tab2 = st.tabs(["Resultate", "Fagenverlauf (History)"])

with tab2:
    st.markdown('<div class="subheader">📜 Vergangene Fragen</div>', unsafe_allow_html=True)
    
    # Display history in a nicer format
    history = history_service.get_history()
    if history:
        for i, q in enumerate(history, start=1):
            st.markdown(f"**{i}.** {q}")
    else:
        st.info("Es gibt noch keinen Frageverlauf.")
    
    # Red clear history button
    if st.button("🗑️ Leere den Frageverlauf", type="secondary", key="clear_history"):
        history_service.clear_history()
        st.success("Wir haben den Fageverlauf geleert!")

# Async function to run browser agent
async def run_agent_with_logstream(task, log_callback):
    initial_actions = [{'open_tab': {'url': 'https://compendium.ch/'}}]

    openai_key = st.secrets["openai"]["open_ai_key"]
    llm = ChatOpenAI(model="gpt-4o", openai_api_key=openai_key)

    # Use the existing log file path
    log_path = "logs/conversation/last_run.txt"

    # Delete old log file if it exists
    if os.path.exists(log_path):
        os.remove(log_path)

    agent = Agent(
        task=task,
        initial_actions=initial_actions,
        llm=llm,
        browser=browser,
        save_conversation_path="logs/conversation"
    )

    # Start the agent in the background
    agent_task = asyncio.create_task(agent.run())

    # Stream the log file as it's being written
    last_position = 0
    while not agent_task.done():
        if os.path.exists(log_path):
            async with aiofiles.open(log_path, 'r') as f:
                await f.seek(last_position)
                new_content = await f.read()
                last_position = await f.tell()
                if new_content.strip():
                    log_callback(new_content)
        await asyncio.sleep(0.5)  # Check for updates every 0.5 seconds

    await agent_task
    return agent.history

# Run the Browser Agent when button is clicked
if run_button:
    with tab1:
        if "question" in st.session_state and st.session_state.question:
            log_area = st.empty()

            # Ensure session state var exists
            if "log_text" not in st.session_state:
                st.session_state["log_text"] = ""

            with st.spinner("🔍 Suche läuft..."):

                def update_logs(new_log):
                    st.session_state["log_text"] += new_log
                    log_area.code(st.session_state["log_text"])

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result_history = loop.run_until_complete(
                    run_agent_with_logstream(st.session_state.question, update_logs)
                )
                loop.close()

            st.markdown('<div class="subheader">🔍 Such Resultate</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            st.markdown("### 📋 Agent Output")
            st.write(result_history.final_result())
            st.markdown("</div>", unsafe_allow_html=True)

            with st.expander("📊 Details"):
                st.write("**URLs die besucht wurden:**")
                st.write(result_history.urls())
                
                st.write("**Actionen welche ausgeführt wurden:**")
                st.write(result_history.action_names())
                
                if result_history.errors():
                    st.error("**Errors die wir bekamen:**")
                    st.write(result_history.errors())
        else:
            st.warning("⚠️ Bitte zuerst eine Frage stellen.")