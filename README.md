# Compendium.ch Chatbot

Ein interaktiver Browser-Agent, der automatisiert Informationen über Medikamente von der Website [compendium.ch](https://compendium.ch/) abruft. Stelle Fragen wie "Was ist die Wirkung von Dafalgan?" und erhalte direkt Antworten durch intelligente Browser-Navigation und ein Large Language Model (LLM) erreichbar via: https://compendium-bot.streamlit.app/

![image](https://github.com/user-attachments/assets/4ff19e74-f1da-4bbf-a9e1-14ea13e04053)


---

## 🔍 Features

- 🧠 **Frage-Antwort-System:** Stelle medizinbezogene Fragen und erhalte strukturierte Antworten.
- 🧭 **Browser-Automatisierung:** Erkenntnisse direkt von [compendium.ch](https://compendium.ch).
- 📚 **Fragen-Historie:** Übersicht vergangener Anfragen.
- 🎨 **Custom UI:** Streamlit-basiertes Design mit dunklem und hellem Modus.
- 🔒 **.env & Secrets:** OpenAI Key sicher hinterlegt.

---

## 🚀 Installation & Setup

### 1. Repository klonen

```bash
git clone https://github.com/dein-benutzername/compendium-bot.git
cd compendium-bot
```

### 2. Virtuelle Umgebung einrichten und Abhängigkeiten installieren
```python
python -m venv venv
source venv/bin/activate   # Für Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Playwright installieren (für automatisierte Browser-Steuerung)
```python
playwright install
playwright install-deps
```

### 4. API-Key konfigurieren
Erstelle .streamlit/secrets.toml - mit dem OpenAI key
```toml
[openai]
open_ai_key = "dein-openai-key"
```
### 5. Anwedung
```python
streamlit run main.py
```



