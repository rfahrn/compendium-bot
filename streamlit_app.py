import streamlit as st
import history_questions

st.title("Simple Streamlit App")
st.write("This is a simple Streamlit app that demonstrates the use of a slider and a button.")

question = st.text_input("Enter your question:")

if question:
    st.write("You asked:", question)
    history_questions.add_question(question)
    st.write("History of questions asked:")
    history = history_questions.get_history()
    for i, q in enumerate(history):
        st.write(f"{i+1}. {q}")
