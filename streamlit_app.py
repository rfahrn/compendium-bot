import streamlit as st
import history_questions
from history_questions import HistoryQuestions


st.set_page_config(page_title="💊 Compendium Bot", layout="centered")
st.title("💊 Compendium Bot")
st.write("This is a simple Streamlit app that demonstrates the use of a slider and a button.")

question = st.text_input("Was möchtest du wissen?", placeholder="z. B. Wirkung von Dafalgan, Dosierung etc.")
history_questions = history_questions.HistoryQuestions(question)
# option setting for if user want to see history of questions asked

show_history = st.checkbox("Show history of questions asked", value=False)
if show_history:
    history_questions.load_history()
    st.write("History of questions asked:")
    history = history_questions.get_history()
    for i, q in enumerate(history):
        st.write(f"{i+1}. {q}")
#             history = f.readlines()

# give also option to clear history of questions asked
clear_history = st.button("Clear history of questions asked")
if clear_history:
    history_questions.clear_history()
    st.write("History cleared.")


"""
if question:
    st.write("You asked:", question)
    history_questions.add_question(question)
    st.write("History of questions asked:")
    history = history_questions.get_history()
    for i, q in enumerate(history):
        st.write(f"{i+1}. {q}")
"""