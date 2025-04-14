import streamlit as st
import asyncio
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from browser_use import Agent

def main():
    st.title("Browser Use + Streamlit Demo")
    if "agent_result" not in st.session_state:
        st.session_state["agent_result"] = None
    user_task = st.text_input("Enter your Agent Task", value="Compare the price of gpt-4o and DeepSeek-V3")
    if st.button("Run Agent"):
        async def run_agent(task):
            import os, streamlit as st
            os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
            print("OPENAI_API_KEY", os.environ["OPENAI_API_KEY"])
            inital_actions = [
        {'open_tab':{'url': 'https://compendium.ch/'}}]
            llm = ChatOpenAI(model="gpt-4o", temperature=0.0,openai_api_key=st.secrets["OPENAI_API_KEY"])
            
            agent = Agent(
                task=task,
                initial_actions=inital_actions,
                llm=llm,)


            history = await agent.run()
            return history

        loop = asyncio.new_event_loop()
        result_history = loop.run_until_complete(run_agent(user_task))
        loop.close()

        st.session_state["agent_result"] = result_history

    if st.session_state["agent_result"] is not None:
        st.write("**Agent Final Output**:")
        final_output = st.session_state["agent_result"].final_result()
        st.write(final_output)
        st.write("**URLs Visited**:", st.session_state["agent_result"].urls())
        st.write("**Action Names**:", st.session_state["agent_result"].action_names())
        st.write("**Any Errors?**:", st.session_state["agent_result"].errors())

if __name__ == "__main__":
    main()
