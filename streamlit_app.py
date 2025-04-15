import streamlit as st
import os
import asyncio
from dotenv import load_dotenv
from history_questions import HistoryQuestions
from browser_use import BrowserConfig, Agent, Browser
from browser_use.browser.context import BrowserContextConfig
from langchain_openai import ChatOpenAI
import subprocess

# Install Playwright if needed
#os.system("playwright install --force")

# Load environment variables
load_dotenv()

# Initialize Streamlit page
st.set_page_config(page_title="💊 Compendium Bot", layout="centered")
st.title("💊 Compendium Bot")

# Setup the browser
config = BrowserConfig(headless=True)
browser = Browser(config=config)

# Initialize HistoryQuestions service
history_service = HistoryQuestions()

st.write("This is a simple Streamlit app that demonstrates storing a question history.")

# Text input for the question
question = st.text_input(
    "Was möchtest du wissen?",
    placeholder="z. B. Wirkung von Dafalgan, Dosierung etc."
)

# Store question in session and add to history
if question:
    history_service.add_question(question)
    st.write(f"Du hast gefragt: *{question}*")
    st.session_state.question = question

# Show history toggle
show_history = st.checkbox("Show history of questions asked", value=False)
if show_history:
    st.subheader("History of questions asked")
    history = history_service.get_history()
    if history:
        for i, q in enumerate(history, start=1):
            st.write(f"{i}. {q}")
    else:
        st.write("No history available.")

# Clear history button
if st.button("Clear history of questions asked"):
    history_service.clear_history()
    st.success("History cleared.")

# Async function to run browser agent
async def run_agent(task):
    initial_actions = [{'open_tab': {'url': 'https://compendium.ch/'}}]

    # Use OpenAI key from st.secrets or .env
    openai_key = st.secrets["openai"]["open_ai_key"]
    llm = ChatOpenAI(model="gpt-4o", openai_api_key=openai_key)

    agent = Agent(
        task=task,
        initial_actions=initial_actions,
        llm=llm,
        browser=browser
    )

    history = await agent.run()
    return history

# Run the Browser Agent directly
if st.button("Run Browser Agent"):
    if "question" in st.session_state and st.session_state.question:
        with st.spinner("Running agent..."):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result_history = loop.run_until_complete(run_agent(st.session_state.question))
            loop.close()

        st.write("**Agent Final Output**:")
        st.write(result_history.final_result())

        st.write("**URLs Visited**:")
        st.write(result_history.urls())

        st.write("**Action Names**:")
        st.write(result_history.action_names())

        st.write("**Any Errors?**:")
        st.write(result_history.errors())
    else:
        st.warning("No question available to pass to the browser agent.")
