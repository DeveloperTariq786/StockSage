from google.adk.tools import FunctionTool
import os
import requests

def fetch_tweets(ticker: str) -> dict:
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
    if not bearer_token or bearer_token == "your_twitter_bearer_token":
        return {"error": "Twitter API token not configured", "tweets": []}
    
    headers = {"Authorization": f"Bearer {bearer_token}"}
    query = f"{ticker} stock"
    url = f"https://api.twitter.com/2/tweets/search/recent?query={query}&max_results=10"
    response = requests.get(url, headers=headers)
    tweets = response.json().get("data", [])
    return {"ticker": ticker, "tweets": tweets}

fetch_tweets = FunctionTool(fetch_tweets)
