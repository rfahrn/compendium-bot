# tools/tavily_live_rag.py

import os
import requests
import openai
from bs4 import BeautifulSoup
from tavily import TavilyClient

openai.api_key = os.getenv('OPENAI_KEY')
tavily_client = TavilyClient(api_key=os.getenv('TAVILY_API_KEY'))
client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
def tavily_web_search_urls(query, num_results=3):
    try:
        results = client.search(
            query=query,
            search_depth="advanced",
            include_answer="advanced",
            max_results=num_results,
            include_images=True,
            include_image_descriptions=True,
            include_raw_content=True,
        )
        urls = [item.get("url") for item in results.get("results", [])]
        return urls
    except Exception as e:
        print(f"❗ Fehler bei Tavily Websuche: {e}")
        return []

def scrape_page(url):
    try:
        response = requests.get(url, timeout=7)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator="\n", strip=True)
        return text
    except Exception as e:
        print(f"⚠️ Fehler beim Abrufen der Seite {url}: {e}")
        return ""

def summarize_from_scraped_pages(user_question, pages_texts):
    combined_context = "\n\n".join(pages_texts)

    system_message = "Du bist ein hochspezialisierter medizinischer Assistent. Antworte IMMER auf Deutsch, nur präzise und fachlich exakt. Wenn die Frage nach einer bestimmten Kategorie (z.B. Wirkung, Dosierung, Lagerung) fragt, darfst du nur diese Information angeben."

    user_prompt = f"""
Hier sind Inhalte von verschiedenen Webseiten. 

⚡ Achtung: Beantworte nur die folgende medizinische Frage und ignoriere alles andere. Gehe NICHT auf Nebenwirkungen, Rechtsfragen oder irrelevante Details ein, wenn nicht explizit gefragt.

Frage: {user_question}

Webseiteninhalte:
{combined_context}

✅ Beschränke dich strikt auf die Wirkung ("Was bewirkt das Medikament?") falls die Frage nach Wirkung fragt.
✅ Wenn nichts Relevantes gefunden wird, gib höflich an, dass keine direkte Information verfügbar war.
✅ Antworte kompakt und präzise.

"""
    response = openai.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_prompt}
        ]
    )

    return response.choices[0].message.content

def smart_tavily_answer(user_question, num_results=3):
    """Full smart Tavily search -> scrape -> GPT summarize pipeline."""
    print("🌐 Starte Websuche über Tavily...")

    urls = tavily_web_search_urls(user_question, num_results=num_results)
    if not urls:
        return "❗ Keine Webseiten gefunden."

    print(f"🔗 Gefundene Links: {urls}")

    pages_texts = []
    for idx, url in enumerate(urls, start=1):
        print(f"📄 Lade Seite {idx}: {url}")
        text = scrape_page(url)
        if text:
            pages_texts.append(text)

    if not pages_texts:
        return "❗ Keine brauchbaren Inhalte von den Webseiten abrufbar."

    print("🧠 Erstelle Zusammenfassung basierend auf Webseiten...")
    answer = summarize_from_scraped_pages(user_question, pages_texts)

    # Optionally also return the URLs used
    urls_list = "\n".join([f"- {url}" for url in urls])
    final_answer = f"{answer}\n\n🔗 **Verwendete Quellen:**\n{urls_list}"

    return final_answer
