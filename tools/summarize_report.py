from google.adk.tools import FunctionTool

def analyze_technical_signals(tech_indicators):
    signals = []
    if tech_indicators["is_above_sma_50"]:
        signals.append("Price above 50-day moving average indicates short-term uptrend")
    else:
        signals.append("Price below 50-day moving average suggests short-term weakness")
        
    if tech_indicators["is_above_sma_200"]:
        signals.append("Price above 200-day moving average confirms long-term uptrend")
    else:
        signals.append("Price below 200-day moving average indicates bear market")
        
    rsi = tech_indicators["rsi"]
    if rsi > 70:
        signals.append(f"RSI at {rsi} suggests overbought conditions")
    elif rsi < 30:
        signals.append(f"RSI at {rsi} indicates oversold conditions")
    else:
        signals.append(f"RSI at {rsi} shows neutral momentum")
        
    return signals

def analyze_fundamentals(data):
    analysis = []
    
    # Valuation Analysis
    if data["pe_ratio"]:
        if data["pe_ratio"] > 25:
            analysis.append("High P/E ratio suggests expensive valuation")
        elif data["pe_ratio"] < 15:
            analysis.append("Low P/E ratio indicates potential value opportunity")
            
    # Financial Health
    if data["debt_to_equity"]:
        if data["debt_to_equity"] > 2:
            analysis.append("High debt-to-equity ratio raises concerns")
        elif data["debt_to_equity"] < 0.5:
            analysis.append("Strong balance sheet with low leverage")
            
    # Profitability
    if data["profit_margins"]:
        if data["profit_margins"] > 0.2:
            analysis.append("Excellent profit margins indicate strong business model")
        elif data["profit_margins"] < 0.05:
            analysis.append("Thin profit margins suggest competitive pressures")
            
    return analysis

def determine_recommendation(tech_signals, fundamental_analysis, data):
    bullish_points = 0
    bearish_points = 0
    
    # Technical Score
    if data["technical_indicators"]["is_above_sma_50"]:
        bullish_points += 1
    if data["technical_indicators"]["is_above_sma_200"]:
        bullish_points += 2
    if 30 < data["technical_indicators"]["rsi"] < 70:
        bullish_points += 1
    elif data["technical_indicators"]["rsi"] > 70:
        bearish_points += 2
    elif data["technical_indicators"]["rsi"] < 30:
        bullish_points += 2
        
    # Fundamental Score
    if data["pe_ratio"] and data["pe_ratio"] < 15:
        bullish_points += 2
    elif data["pe_ratio"] and data["pe_ratio"] > 25:
        bearish_points += 2
        
    if data["profit_margins"] and data["profit_margins"] > 0.2:
        bullish_points += 2
    elif data["profit_margins"] and data["profit_margins"] < 0.05:
        bearish_points += 2
        
    # Determine recommendation
    score = bullish_points - bearish_points
    if score >= 4:
        return "STRONG BUY", 90
    elif score >= 2:
        return "BUY", 75
    elif score <= -4:
        return "STRONG SELL", 90
    elif score <= -2:
        return "SELL", 75
    else:
        return "HOLD", 60

def summarize_report(data: dict) -> dict:
    ticker = list(data.keys())[0]
    stock_data = data[ticker]
    
    # Perform analysis
    technical_signals = analyze_technical_signals(stock_data["technical_indicators"])
    fundamental_analysis = analyze_fundamentals(stock_data)
    recommendation, confidence = determine_recommendation(technical_signals, fundamental_analysis, stock_data)
    
    # Combine all insights
    summary = f"{ticker} Analysis Summary:\n"
    summary += f"Current Price: ${stock_data['current_price']}\n"
    summary += "\nTechnical Analysis:\n- " + "\n- ".join(technical_signals)
    summary += "\n\nFundamental Analysis:\n- " + "\n- ".join(fundamental_analysis)
    
    return {
        "summary": summary,
        "recommendation": recommendation,
        "confidence": confidence,
        "technical_signals": technical_signals,
        "fundamental_analysis": fundamental_analysis
    }

summarize_report = FunctionTool(summarize_report)
