from langchain_openai import ChatOpenAI
from browser_use import Agent
import asyncio
from dotenv import load_dotenv

load_dotenv()

def get_latest_question(history_file="history.txt"):
    """Read the latest question from the history file."""
    try:
        with open(history_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return lines[-1].strip() if lines else None
    except Exception as e:
        print(f"Error reading history file: {e}")
        return None

async def main():
    question = get_latest_question()
    if not question:
        print("No question found in history.")
        return
    inital_actions = [
        {'open_tab':{'url': 'https://compendium.ch/'}}]
    agent = Agent(
        task=question,
        initial_actions = inital_actions,
        llm=ChatOpenAI(model="gpt-4o"),
    )
    await agent.run()

asyncio.run(main())