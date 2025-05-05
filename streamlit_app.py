import streamlit as st
import os
import asyncio
from dotenv import load_dotenv
from history_questions import HistoryQuestions
from browser_use import BrowserConfig, Agent, Browser
from browser_use.browser.context import BrowserContextConfig
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

# Streamlit config
st.set_page_config(
    page_title="💊 Compendium Bot",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS styles
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; margin-bottom: 1.5rem; }
    .subheader { font-size: 1.5rem; margin-top: 2rem; margin-bottom: 1rem; }
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

# Header
st.markdown('<div class="main-header">💊 Compendium Bot</div>', unsafe_allow_html=True)
st.markdown("Dieser Bot kann im Compendium nach Medikamenteninformationen suchen. Stelle eine Frage zu einem Medikament, um zu beginnen.")

# Browser and history
config = BrowserConfig(headless=True)
browser = Browser(config=config)
history_service = HistoryQuestions()

# Layout
col1, col2 = st.columns([3, 1])
with col1:
    question = st.text_input("Was möchtest du wissen?", placeholder="z. B. Wirkung von Dafalgan, Dosierung etc.")
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    run_button = st.button("🚀 Anfrage starten")

# Save question
if question:
    history_service.add_question(question)
    st.session_state.question = question
    st.write(f"Du hast gefragt: *{question}*")

# Tabs
tab1, tab2 = st.tabs(["Resultate", "Fragenverlauf (History)"])

with tab2:
    st.markdown('<div class="subheader">📜 Vergangene Fragen</div>', unsafe_allow_html=True)
    history = history_service.get_history()
    if history:
        for i, q in enumerate(history, start=1):
            st.markdown(f"**{i}.** {q}")
    else:
        st.info("Es gibt noch keinen Frageverlauf.")
    if st.button("🗑️ Leere den Frageverlauf"):
        history_service.clear_history()
        st.success("Fragenverlauf wurde geleert!")

# Async agent function
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

# Agent run block
if run_button:
    with tab1:
        if "question" in st.session_state:
            with st.spinner("🔍 Suche läuft..."):
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result_history = loop.run_until_complete(run_agent(st.session_state.question))
                    loop.close()
                except Exception as e:
                    st.error(f"❌ Fehler beim Agentenlauf: {e}")
                    result_history = None

            if result_history:
                # 📋 Final result
                st.markdown('<div class="subheader">📋 Endgültige Antwort</div>', unsafe_allow_html=True)
                st.markdown('<div class="result-box">', unsafe_allow_html=True)
                try:
                    final_output = result_history.final_result()
                    if final_output:
                        st.markdown(final_output if isinstance(final_output, str) else str(final_output))
                    else:
                        st.warning("⚠️ Keine finale Antwort erhalten.")
                except Exception as e:
                    st.error(f"Fehler beim Anzeigen der Antwort: {e}")
                st.markdown('</div>', unsafe_allow_html=True)

                # 📊 Details
                st.markdown('<div class="subheader">📊 Details zum Agentenlauf</div>', unsafe_allow_html=True)
                st.markdown('<div class="result-box">', unsafe_allow_html=True)

                # 🔗 URLs
                st.markdown("### 🔗 Besuchte URLs")
                try:
                    urls = result_history.urls()
                    if urls:
                        for i, url in enumerate(urls, 1):
                            st.markdown(f"[🔗 Link {i}]({url})", unsafe_allow_html=True)
                    else:
                        st.info("Keine URLs besucht.")
                except Exception as e:
                    st.error(f"Fehler beim Abrufen der URLs: {e}")

                # ⚙️ Aktionen
                st.markdown("### ⚙️ Aktionen")
                try:
                    actions = result_history.action_names()
                    if actions:
                        for action in actions:
                            st.markdown(f"- {action}")
                    else:
                        st.info("Keine Aktionen aufgezeichnet.")
                except Exception as e:
                    st.error(f"Fehler beim Abrufen der Aktionen: {e}")

                # ❗ Fehler
                st.markdown("### ❗ Fehler")
                try:
                    errors = result_history.errors()
                    if errors:
                        for err in errors:
                            st.error(err)
                    else:
                        st.success("Keine Fehler festgestellt.")
                except Exception as e:
                    st.error(f"Fehler beim Abrufen der Fehlerdaten: {e}")

                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("⚠️ Keine Antwort vom Agent erhalten.")
        else:
            st.warning("Bitte zuerst eine Frage stellen.")

