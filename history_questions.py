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
    def __init__(self, history_file="history.txt"):
        """
        Initialize the HistoryQuestions class.
        
        Args:
            history_file (str): Path to the history file.
        """
        self.history = []
        self.history_file = history_file
        self.load_history()

    def add_question(self, question):
        """
        Adds a question to the history list and saves it.
        """
        if question and question.strip():
            question = question.strip()
            self.history.append(question)
            # Save immediately to keep file in sync
            try:
                with open(self.history_file, "a") as f:
                    f.write(question + "\n")
                print(f"Question added: {question}")
            except Exception as e:
                print(f"Error saving question: {str(e)}")
        else:
            print("Cannot add empty question.")

    def get_history(self):
        """
        Retrieves and displays the history of questions asked.
        Always reloads from file to ensure latest data.
        """
        # Reload from file to ensure we have the most current data
        self.load_history()
        
        if not self.history:
            print("No questions in history.")
            return []
        
        print("\n=== Question History ===")
        for i, question in enumerate(self.history, 1):
            print(f"{i}. {question}")
        return self.history
    
    def clear_history(self):
        """
        Clears the history of questions asked.
        """
        confirm = input("Are you sure you want to clear all history? (y/n): ")
        if confirm.lower() == 'y':
            self.history = []
            with open(self.history_file, "w") as f:
                f.write("")
            print("History cleared successfully.")
        else:
            print("Clear operation cancelled.")
        
    def save_history(self):
        """
        Saves the history to a file.
        """
        with open(self.history_file, "w") as f:
            for question in self.history:
                f.write(question + "\n")
        print(f"History saved to {self.history_file}")
                
    def load_history(self):
        """
        Loads the history from a file.
        """
        try:
            with open(self.history_file, "r") as f:
                self.history = [line.strip() for line in f.readlines() if line.strip()]
            if self.history:
                print(f"Loaded {len(self.history)} questions from history.")
        except FileNotFoundError:
            self.history = []
            print(f"No history file found. A new one will be created at {self.history_file}")

    def search_history(self, keyword):
        """
        Searches for questions containing a keyword.
        """
        # Reload to ensure we have latest data
        self.load_history()
        
        results = [q for q in self.history if keyword.lower() in q.lower()]
        if results:
            print(f"\n=== Search results for '{keyword}' ===")
            for i, question in enumerate(results, 1):
                print(f"{i}. {question}")
        else:
            print(f"No questions found containing '{keyword}'")
        return results
