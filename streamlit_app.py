import streamlit as st
import os
import asyncio
from dotenv import load_dotenv
from history_questions import HistoryQuestions
from browser_use import BrowserConfig, Agent, Browser
from browser_use.browser.context import BrowserContextConfig
from langchain_openai import ChatOpenAI

# Install dependencies
os.system("playwright install")
os.system("playwright install-deps")

# Load environment variables
load_dotenv()

# Streamlit page config
st.set_page_config(
    page_title="💊 Compendium Bot",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS styles
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
        color: #31333F;
    }
    [data-testid="stAppViewContainer"] .stTextInput > div > div > input {
        color: black !important;
    }
    [data-testid="stMarkdownContainer"] {
        color: inherit;
    }
    .result-box {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-top: 1rem;
    }
    [data-theme="dark"] .result-box {
        background-color: #262730;
    }
</style>
""", unsafe_allow_html=True)

# Main title
st.markdown('<div class="main-header">💊 Compendium Bot</div>', unsafe_allow_html=True)

# Description
st.markdown("""
Dieser Bot kann im Compendium nach Medikamenteninformationen suchen.  
Stelle eine Frage zu einem Medikament, um zu beginnen.
""")

# Setup browser and history
config = BrowserConfig(headless=True)
browser = Browser(config=config)
history_service = HistoryQuestions()

# Layout input
col1, col2 = st.columns([3, 1])
with col1:
    question = st.text_input(
        "Was möchtest du wissen?",
        placeholder="z. B. Wirkung von Dafalgan, Dosierung etc."
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    run_button = st.button("🚀 Browser Agent starten", type="primary", key="run_agent")

# Store and display question
if question:
    history_service.add_question(question)
    st.write(f"Du hast gefragt: *{question}*")
    st.session_state.question = question

# Tabs for results and history
tab1, tab2 = st.tabs(["Resultate", "Fragenverlauf (History)"])

with tab2:
    st.markdown('<div class="subheader">📜 Vergangene Fragen</div>', unsafe_allow_html=True)
    history = history_service.get_history()
    if history:
        for i, q in enumerate(history, start=1):
            st.markdown(f"**{i}.** {q}")
    else:
        st.info("Es gibt noch keinen Frageverlauf.")

    if st.button("🗑️ Leere den Frageverlauf", type="secondary", key="clear_history"):
        history_service.clear_history()
        st.success("Wir haben den Fragenverlauf geleert!")

# Async agent logic
async def run_agent(task):
    initial_actions = [{'open_tab': {'url': 'https://compendium.ch/'}}]
    openai_key = st.secrets["openai"]["open_ai_key"]
    llm = ChatOpenAI(model="gpt-4o", openai_api_key=openai_key)

    agent = Agent(
        task=task,
        initial_actions=initial_actions,
        llm=llm,
        browser=browser
    )

    return await agent.run()

# Execute agent and show results
if run_button:
    with tab1:
        if "question" in st.session_state and st.session_state.question:
            with st.spinner("🔍 Suche läuft..."):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result_history = loop.run_until_complete(run_agent(st.session_state.question))
                loop.close()

            st.markdown('<div class="subheader">🔍 Such Resultate</div>', unsafe_allow_html=True)
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            st.markdown("### 📋 Agent Output")

            final_output = result_history.final_result()
            if isinstance(final_output, str):
                st.markdown(final_output)
            else:
                st.write(final_output)
            st.markdown("</div>", unsafe_allow_html=True)

            # Detailed breakdown
            with st.expander("📊 Details"):
                st.markdown("### 🔗 Besuchte URLs")
                urls = result_history.urls()
                if urls:
                    for i, url in enumerate(urls, 1):
                        st.markdown(f"[🔗 Link {i}]({url})", unsafe_allow_html=True)
                else:
                    st.info("Keine URLs wurden besucht.")

                st.markdown("---")

                st.markdown("### ⚙️ Aktionen")
                actions = result_history.action_names()
                if actions:
                    for i, action in enumerate(actions, 1):
                        st.markdown(f"- {action}")
                else:
                    st.info("Keine Aktionen wurden ausgeführt.")

                st.markdown("---")

                errors = result_history.errors()
                if errors:
                    st.markdown("### ❗ Fehler")
                    for err in errors:
                        st.error(err)
                else:
                    st.success("Keine Fehler wurden festgestellt.")
        else:
            st.warning("⚠️ Bitte zuerst eine Frage stellen.")
