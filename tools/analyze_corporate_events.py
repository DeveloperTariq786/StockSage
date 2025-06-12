from google.adk.tools import FunctionTool
import yfinance as yf
from datetime import datetime, timedelta
import requests
import os

def analyze_corporate_events(ticker: str) -> dict:
    """Analyzes corporate events and their impact on stock performance."""
    stock = yf.Ticker(ticker)
    
    # Get earnings data
    calendar = stock.calendar
    earnings = stock.earnings
    quarterly_earnings = stock.quarterly_earnings
    
    # Get institutional holders and major shareholders
    major_holders = stock.major_holders
    institutional_holders = stock.institutional_holders
    
    # Get news
    news_api_key = os.getenv("NEWS_API_KEY")
    if not news_api_key:
        raise ValueError("NEWS_API_KEY environment variable is required but not set")
        
    company_name = stock.info.get('longName', ticker)
    
    # Get recent news about corporate events
    query = f"({company_name} OR {ticker}) AND (CEO OR executive OR earnings OR acquisition OR merger OR policy OR regulation OR lawsuit OR quarterly results)"
    url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&apiKey={news_api_key}&language=en"
    
    response = requests.get(url)
    all_news = response.json().get("articles", [])[:20]  # Get top 20 relevant news
    
    # Analyze price changes around news dates
    event_impacts = []
    for news in all_news:
        try:
            news_date = datetime.strptime(news['publishedAt'][:10], '%Y-%m-%d')
            # Get stock prices for 5 days before and after news
            start_date = (news_date - timedelta(days=5)).strftime('%Y-%m-%d')
            end_date = (news_date + timedelta(days=5)).strftime('%Y-%m-%d')
            
            hist = stock.history(start=start_date, end=end_date)
            if not hist.empty:
                price_before = hist['Close'].iloc[0] if len(hist) > 0 else None
                price_after = hist['Close'].iloc[-1] if len(hist) > 0 else None
                if price_before and price_after:
                    price_change = ((price_after - price_before) / price_before) * 100
                    
                    event_impacts.append({
                        "date": news['publishedAt'][:10],
                        "title": news['title'],
                        "description": news['description'],
                        "price_change_percent": round(float(price_change), 2),
                        "url": news['url']
                    })
        except Exception as e:
            continue    # Analyze earnings surprises
    earnings_analysis = []
    if quarterly_earnings is not None:
        for date, row in quarterly_earnings.iterrows():
            try:
                date_str = pd.Timestamp(date).strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date)
                reported_eps = float(row.get('Reported EPS', 0))
                estimated_eps = float(row.get('Estimated EPS', 0))
                
                surprise_percent = 0
                if estimated_eps != 0:
                    surprise_percent = float(((reported_eps - estimated_eps) / abs(estimated_eps)) * 100)
                
                earnings_analysis.append({
                    "date": date_str,
                    "reported_eps": reported_eps,
                    "estimated_eps": estimated_eps,
                    "surprise_percent": surprise_percent
                })
            except Exception as e:
                continue    # Get upcoming events
    upcoming_events = {}
    if calendar is not None:
        for event_type, event_date in calendar.items():
            try:
                if isinstance(event_date, (datetime, pd.Timestamp)):
                    upcoming_events[event_type] = pd.Timestamp(event_date).strftime('%Y-%m-%d')
                elif event_date is not None:
                    upcoming_events[event_type] = str(event_date)
            except Exception as e:
                continue

    # Analyze institutional holdings
    institutional_analysis = []
    if institutional_holders is not None:
        for _, holder in institutional_holders.iterrows():
            institutional_analysis.append({
                "holder": str(holder.get('Holder', '')),
                "shares": int(holder.get('Shares', 0)),
                "date_reported": holder.get('Date Reported', '').strftime('%Y-%m-%d'),
                "percent_out": float(holder.get('% Out', 0)),
                "value": float(holder.get('Value', 0))
            })

    return {
        "company_name": company_name,
        "ticker": ticker,
        "corporate_events": {
            "significant_news": event_impacts,
            "earnings_analysis": earnings_analysis,
            "upcoming_events": upcoming_events,
            "institutional_changes": institutional_analysis
        }
    }

analyze_corporate_events = FunctionTool(analyze_corporate_events)
