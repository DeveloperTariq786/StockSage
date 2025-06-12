from google.adk.tools import FunctionTool
import requests
import os

def fetch_news(ticker: str) -> dict:
    api_key = os.getenv("NEWS_API_KEY")
    query = f"{ticker} stock"
    url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&apiKey={api_key}"
    response = requests.get(url)
    articles = response.json().get("articles", [])[:5]
    return {"ticker": ticker, "articles": articles}

fetch_news = FunctionTool(fetch_news)
