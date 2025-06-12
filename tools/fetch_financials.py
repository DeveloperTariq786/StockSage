from google.adk.tools import FunctionTool
import yfinance as yf
import numpy as np
import pandas as pd

def calculate_rsi(prices, periods=14):
    # Calculate price changes
    changes = np.diff(prices)
    gains = np.where(changes > 0, changes, 0)
    losses = np.where(changes < 0, -changes, 0)
    
    # Calculate average gains and losses
    avg_gain = float(np.mean(gains[:periods]))
    avg_loss = float(np.mean(losses[:periods]))
    
    # Calculate RSI
    rs = float(avg_gain / avg_loss if avg_loss != 0 else 0)
    rsi = float(100 - (100 / (1 + rs)))
    return round(rsi, 2)

def fetch_financials(tickers: list[str]) -> dict:
    result = {}
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Get historical data with error handling
            hist = stock.history(period="1y")
            if hist.empty:
                result[ticker] = {
                    "error": f"No data found for {ticker}. The symbol may be delisted or invalid."
                }
                continue
            
            # Get fundamental ratios
            hist_tail = hist.tail(5)
            history_dict = {}
            for column in hist.columns:
                # Convert numpy values to Python native types
                history_dict[column] = [float(x) for x in hist_tail[column].tolist()]
            history_dates = [pd.Timestamp(dt).strftime('%Y-%m-%d') for dt in hist_tail.index]
            
            # Calculate technical indicators with error handling
            try:
                sma_50 = float(hist['Close'].rolling(window=50).mean().iloc[-1])
                sma_200 = float(hist['Close'].rolling(window=200).mean().iloc[-1])
                rsi = calculate_rsi(hist['Close'].tolist())
            except (IndexError, ValueError) as e:
                sma_50, sma_200, rsi = 0, 0, 0
            
            # Enhanced financial metrics with proper type conversion and error handling
            result[ticker] = {
                # Market Data
                "current_price": float(info.get("regularMarketPrice", 0)),
                "market_cap": int(info.get("marketCap", 0)),
                "volume": int(info.get("volume", 0)),
                "avg_volume": int(info.get("averageVolume", 0)),
                
                # Valuation Metrics
                "pe_ratio": float(info.get("trailingPE", 0)),
                "forward_pe": float(info.get("forwardPE", 0)),
                "peg_ratio": float(info.get("pegRatio", 0)),
                "price_to_book": float(info.get("priceToBook", 0)),
                "enterprise_value": float(info.get("enterpriseValue", 0)),
                
                # Financial Health
                "debt_to_equity": float(info.get("debtToEquity", 0)),
                "current_ratio": float(info.get("currentRatio", 0)),
                "quick_ratio": float(info.get("quickRatio", 0)),
                
                # Profitability
                "profit_margins": float(info.get("profitMargins", 0)),
                "operating_margins": float(info.get("operatingMargins", 0)),
                "roa": float(info.get("returnOnAssets", 0)),
                "roe": float(info.get("returnOnEquity", 0)),
                
                # Growth Metrics
                "revenue_growth": float(info.get("revenueGrowth", 0)),
                "earnings_growth": float(info.get("earningsGrowth", 0)),
                
                # Technical Indicators
                "technical_indicators": {
                    "sma_50": sma_50,
                    "sma_200": sma_200,
                    "rsi": rsi,
                    "is_above_sma_50": bool(info.get("regularMarketPrice", 0) > sma_50),
                    "is_above_sma_200": bool(info.get("regularMarketPrice", 0) > sma_200),
                },
                
                # Historical Data
                "history": {
                    "dates": history_dates,
                    "data": history_dict
                }
            }
        except Exception as e:
            result[ticker] = {
                "error": f"Failed to fetch data for {ticker}: {str(e)}"
            }
            
    return result

fetch_financials = FunctionTool(fetch_financials)
