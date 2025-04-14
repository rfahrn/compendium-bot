import streamlit as st
from langchain_openai import ChatOpenAI
from browser_use import Agent
import asyncio
from dotenv import load_dotenv
import sys

load_dotenv()

def get_latest_question(history_file="history.txt"):
    """Read the latest question from the history file."""
    try:
        with open(history_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return lines[-1].strip() if lines else None
    except Exception as e:
        st.error(f"Error reading history file: {e}")
        return None

async def run_browser_agent(question):
    initial_actions = [
        {'open_tab': {'url': 'https://compendium.ch/'}}
    ]
    agent = Agent(
        task=question,
        initial_actions=initial_actions,
        llm=ChatOpenAI(model="gpt-4o"),
    )
    await agent.run()

def streamlit_app():
    st.title("Browser Agent Controller")
    
    # Input options
    input_option = st.radio("Choose input method:", ["Enter question", "Use latest question from history"])
    
    if input_option == "Enter question":
        question = st.text_input("Enter your question:")
    else:
        question = get_latest_question()
        st.write(f"Latest question: {question}")
    
    if st.button("Run Browser Agent") and question:
        st.write("Starting browser agent...")
        # We need to use a different approach to run async code in Streamlit
        asyncio.run(run_browser_agent(question))
        st.success("Browser agent completed")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--streamlit":
        # This is handled by streamlit run
        pass
    elif len(sys.argv) > 1:
        # Command line mode
        task = sys.argv[1]
        asyncio.run(run_browser_agent(task))
    else:
        # Run Streamlit app
        streamlit_app()