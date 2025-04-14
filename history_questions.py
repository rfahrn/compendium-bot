def add_question(question):
    """
    Adds a question to the history list.
    """
    with open("history.txt", "a") as f:
        f.write(question + "\n")


def get_history():
    """
    Retrieves the history of questions asked.
    """
    try:
        with open("history.txt", "r") as f:
            history = f.readlines()
        # Remove newline characters and return a list of questions
        return [q.strip() for q in history]
    except FileNotFoundError:
        # If the file does not exist, return an empty list
        return []
    