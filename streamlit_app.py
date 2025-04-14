import streamlit as st
from history_questions import HistoryQuestions

st.set_page_config(page_title="💊 Compendium Bot", layout="centered")
st.title("💊 Compendium Bot")

# Initialize HistoryQuestions; by default it uses "history.txt"
history_service = HistoryQuestions()

st.write("This is a simple Streamlit app that demonstrates storing a question history.")

# Text input for the question
question = st.text_input(
    "Was möchtest du wissen?",
    placeholder="z. B. Wirkung von Dafalgan, Dosierung etc."
)

# Whenever the user presses Enter, Streamlit re-runs the script;
# we add the question to history if it isn't empty
if question:
    history_service.add_question(question)
    st.write(f"Du hast gefragt: *{question}*")

# Checkbox to show the history
show_history = st.checkbox("Show history of questions asked", value=False)
if show_history:
    st.subheader("History of questions asked")
    history = history_service.get_history()
    if history:
        for i, q in enumerate(history, start=1):
            st.write(f"{i}. {q}")
    else:
        st.write("No history available.")

# Button to clear the entire history
if st.button("Clear history of questions asked"):
    history_service.clear_history()
    st.success("History cleared.")
