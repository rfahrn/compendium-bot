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

class HistoryQuestions:
    def __init__(self):
        self.history = []

    def add_question(self, question):
        """
        Adds a question to the history list.
        """
        self.history.append(question)

    def get_history(self):
        """
        Retrieves the history of questions asked.
        """
        return self.history
    

    def clear_history(self):
        """
        Clears the history of questions asked.
        """
        self.history = []
        with open("history.txt", "w") as f:
            f.write("")
        
    def save_history(self):
        """
        Saves the history to a file.
        """
        with open("history.txt", "w") as f:
            for question in self.history:
                f.write(question + "\n")
                
    def load_history(self):
        """
        Loads the history from a file.
        """
        try:
            with open("history.txt", "r") as f:
                self.history = [line.strip() for line in f.readlines()]
        except FileNotFoundError:
            self.history = []
