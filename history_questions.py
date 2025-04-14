import os

class HistoryQuestions:
    def __init__(self, history_file="history.txt"):
        self.history_file = history_file
        self.history = []
        self.load_history()

    def add_question(self, question: str):
        """Add a non-empty question to both the in-memory list and file."""
        question = question.strip()
        if question:
            self.history.append(question)
            try:
                with open(self.history_file, "a", encoding="utf-8") as f:
                    f.write(question + "\n")
            except Exception as e:
                print(f"Error writing to file: {e}")

    def get_history(self):
        """Return the latest in-memory list of questions."""
        # Reload to ensure we pick up any external changes
        self.load_history()
        return self.history

    def clear_history(self):
        """Clear the entire history and empty the file."""
        self.history = []
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                f.write("")
        except Exception as e:
            print(f"Error clearing file: {e}")

    def load_history(self):
        """Load questions from the file into memory."""
        if not os.path.exists(self.history_file):
            self.history = []
            return

        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            self.history = [line.strip() for line in lines if line.strip()]
        except Exception as e:
            print(f"Error loading file: {e}")
            self.history = []
