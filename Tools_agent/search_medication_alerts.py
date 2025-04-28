from tavily import TavilyClient
import os

# Initialize Tavily Client
client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search_medication_alerts(medication, num_results=5):
    """Search for recent news alerts about a medication."""
    try:
        print(f"🚨 Suche nach aktuellen Warnungen für '{medication}'...")

        # Create a focused search query
        alert_query = f"{medication} FDA recall warning safety side effects site:fda.gov OR site:ema.europa.eu OR site:reuters.com OR site:cnn.com"
        
        results = client.search(
            query=alert_query,
            search_depth="advanced",
            include_answer=False,
            max_results=num_results,
        )
        
        alerts = results.get("results", [])

        if not alerts:
            return "✅ Keine aktuellen Warnungen gefunden."

        alert_response = "**🚨 Aktuelle Warnungen und Nachrichten:**\n\n"
        for idx, alert in enumerate(alerts, 1):
            title = alert.get("title", "Kein Titel")
            url = alert.get("url", "Kein Link")
            published = alert.get("published_date", "Unbekanntes Datum")
            alert_response += f"{idx}. [{title}]({url}) - 📅 {published}\n"

        return alert_response
    
    except Exception as e:
        print(f"❗ Fehler bei der Alerts-Suche: {e}")
        return "❗ Fehler bei der Suche nach aktuellen Warnungen."
