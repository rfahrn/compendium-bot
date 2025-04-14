import streamlit as st
import history_questions



st.set_page_config(page_title="💊 Compendium Bot", layout="centered")
st.write("This is a simple Streamlit app that demonstrates the use of a slider and a button.")

question = st.text_input("Was möchtest du wissen?", placeholder="z. B. Wirkung von Dafalgan, Dosierung etc.")
if question:
    st.write("You asked:", question)
    history_questions.add_question(question)
    st.write("History of questions asked:")
    history = history_questions.get_history()
    for i, q in enumerate(history):
        st.write(f"{i+1}. {q}")
