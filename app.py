import streamlit as st
import asyncio

# For environment variables (if you use a .env)
from dotenv import load_dotenv
load_dotenv()

# Import your LLM & Browser Use
from langchain_openai import ChatOpenAI
from browser_use import Agent

def main():
    st.title("Browser Use + Streamlit Demo")

    # Keep track of the final agent output in session
    if "agent_result" not in st.session_state:
        st.session_state["agent_result"] = None

    # Let user specify a quick "task" for the agent
    user_task = st.text_input("Enter your Agent Task", value="Compare the price of gpt-4o and DeepSeek-V3")

    # Button to run the agent
    if st.button("Run Agent"):
        # Because Agent.run() is async, define an async helper:
        async def run_agent(task):
            # 1) Instantiate the LLM
            llm = ChatOpenAI(model="gpt-4o", temperature=0.0)
            
            # 2) Create the agent
            agent = Agent(
                task=task,
                llm=llm,
                # you could also set other parameters, e.g. use_vision=False
            )
            
            # 3) Run it
            history = await agent.run()

            # 4) Return the entire AgentHistoryList
            return history

        # Create a fresh event loop and run the agent:
        loop = asyncio.new_event_loop()
        result_history = loop.run_until_complete(run_agent(user_task))
        loop.close()

        st.session_state["agent_result"] = result_history

    # If we have a result, display it
    if st.session_state["agent_result"] is not None:
        st.write("**Agent Final Output**:")
        final_output = st.session_state["agent_result"].final_result()
        st.write(final_output)

        # If you want to see steps, visited URLs, etc:
        st.write("**URLs Visited**:", st.session_state["agent_result"].urls())
        st.write("**Action Names**:", st.session_state["agent_result"].action_names())
        st.write("**Any Errors?**:", st.session_state["agent_result"].errors())

if __name__ == "__main__":
    main()
