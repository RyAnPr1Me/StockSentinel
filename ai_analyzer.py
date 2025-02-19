import os
from datetime import datetime
import pandas as pd
import json
#from openai import OpenAI #Removed as per intention

def calculate_analysis(hist_data, metrics, info):
    """
    Generate comprehensive stock analysis based on technical indicators
    """
    # Get latest data points
    current_price = hist_data['Close'].iloc[-1]
    prev_price = hist_data['Close'].iloc[-2]
    ma_20 = hist_data['MA20'].iloc[-1]
    ma_50 = hist_data['MA50'].iloc[-1]
    rsi = hist_data['RSI'].iloc[-1]
    volume = hist_data['Volume'].iloc[-1]
    avg_volume = hist_data['Volume'].rolling(window=20).mean().iloc[-1]

    # Price trend analysis
    price_trend = "bullish" if current_price > ma_50 else "bearish"
    momentum = "increasing" if current_price > ma_20 else "decreasing"
    volume_trend = "high" if volume > avg_volume * 1.2 else "low" if volume < avg_volume * 0.8 else "normal"

    # Generate recommendation
    signals = {
        'price_above_ma50': current_price > ma_50,
        'price_above_ma20': current_price > ma_20,
        'rsi_oversold': rsi < 30,
        'rsi_overbought': rsi > 70,
        'volume_high': volume > avg_volume * 1.2
    }

    # Determine recommendation
    if (signals['price_above_ma50'] and signals['price_above_ma20'] and not signals['rsi_overbought']) or \
       (signals['rsi_oversold'] and signals['volume_high']):
        recommendation = "Buy"
        risk_level = "Medium"
    elif signals['rsi_overbought'] or (not signals['price_above_ma50'] and not signals['price_above_ma20']):
        recommendation = "Sell"
        risk_level = "High"
    else:
        recommendation = "Hold"
        risk_level = "Low"

    # Calculate price volatility
    returns = hist_data['Close'].pct_change()
    volatility = returns.std() * (252 ** 0.5)  # Annualized volatility

    # Prepare analysis components
    summary = f"The stock is currently in a {price_trend} trend with {momentum} momentum. "
    summary += f"Trading volume is {volume_trend} compared to the 20-day average. "
    summary += f"Annual volatility is {volatility:.2%}."

    technical_analysis = f"""
    Price Analysis:
    - Current price (${current_price:.2f}) is {price_trend} relative to the 50-day moving average (${ma_50:.2f})
    - 20-day moving average: ${ma_20:.2f}
    - RSI at {rsi:.2f} indicates {'oversold' if rsi < 30 else 'overbought' if rsi > 70 else 'neutral'} conditions
    - Volume is {volume_trend.upper()} at {volume:,.0f} shares
    """

    fundamental_analysis = f"""
    Market Metrics:
    - Market Cap: {metrics.get('Market Cap', 'N/A')}
    - P/E Ratio: {metrics.get('P/E Ratio', 'N/A')}
    - Beta: {metrics.get('Beta', 'N/A')}

    Sector: {info.get('sector', 'N/A')}
    Industry: {info.get('industry', 'N/A')}
    """

    reasoning = f"""
    Recommendation based on:
    - Price trend: {price_trend.upper()}
    - RSI: {rsi:.2f}
    - Volume: {volume_trend.upper()}
    - Volatility: {volatility:.2%}
    """

    return {
        "summary": summary,
        "technical_analysis": technical_analysis,
        "fundamental_analysis": fundamental_analysis,
        "recommendation": recommendation,
        "risk_level": risk_level,
        "reasoning": reasoning
    }

# Renamed function to use our new approach
def get_stock_analysis(hist_data, metrics, info):
    """Generate analysis for the stock"""
    try:
        return calculate_analysis(hist_data, metrics, info)
    except Exception as e:
        return {
            "error": f"Failed to generate analysis: {str(e)}",
            "summary": "Technical analysis based on price trends and indicators.",
            "technical_analysis": "Analysis temporarily unavailable.",
            "fundamental_analysis": "Analysis temporarily unavailable.",
            "recommendation": "Hold",
            "risk_level": "Medium",
            "reasoning": "Insufficient data for detailed analysis."
        }

def calculate_basic_analysis(hist_data, metrics):
    """Provide basic analysis when AI is unavailable"""
    current_price = hist_data['Close'].iloc[-1]
    ma_50 = hist_data['MA50'].iloc[-1]
    rsi = hist_data['RSI'].iloc[-1]

    # Basic technical analysis
    price_trend = "bullish" if current_price > ma_50 else "bearish"

    # Basic recommendation based on RSI and price trend
    recommendation = "Hold"
    if rsi < 30 and price_trend == "bullish":
        recommendation = "Buy"
    elif rsi > 70 and price_trend == "bearish":
        recommendation = "Sell"

    return {
        "summary": "Basic technical analysis based on price trends and RSI indicator.",
        "technical_analysis": f"Current price is {price_trend} relative to 50-day moving average. RSI at {rsi:.2f} indicates {'oversold' if rsi < 30 else 'overbought' if rsi > 70 else 'neutral'} conditions.",
        "fundamental_analysis": "Fundamental analysis unavailable without AI service.",
        "recommendation": recommendation,
        "risk_level": "Medium",
        "reasoning": "Based on technical indicators only. For comprehensive analysis, please try again later when AI service is available."
    }

def prepare_analysis_prompt(hist_data, metrics, info):
    """Prepare a comprehensive prompt for AI analysis"""
    # Calculate recent performance metrics
    current_price = hist_data['Close'].iloc[-1]
    prev_price = hist_data['Close'].iloc[-2]
    price_change = ((current_price - prev_price) / prev_price) * 100

    # Calculate 50-day moving average
    ma_50 = hist_data['Close'].rolling(window=50).mean().iloc[-1]

    # Prepare the prompt
    prompt = f"""Analyze this stock based on the following data and provide a clear buy/hold/sell recommendation:

Technical Indicators:
- Current Price: ${current_price:.2f}
- 24h Price Change: {price_change:.2f}%
- 50-day Moving Average: ${ma_50:.2f}
- RSI: {hist_data['RSI'].iloc[-1]:.2f}

Key Metrics:
- Market Cap: {metrics.get('Market Cap', 'N/A')}
- P/E Ratio: {metrics.get('P/E Ratio', 'N/A')}
- Forward P/E: {metrics.get('Forward P/E', 'N/A')}
- Beta: {metrics.get('Beta', 'N/A')}

Company Info:
- Sector: {info.get('sector', 'N/A')}
- Industry: {info.get('industry', 'N/A')}

Provide a structured analysis with:
1. Summary of current position
2. Technical analysis
3. Fundamental analysis
4. Clear recommendation (Buy/Hold/Sell)
5. Risk assessment (Low/Medium/High)

Format the response as JSON with these keys: 
summary, technical_analysis, fundamental_analysis, recommendation, risk_level, reasoning
"""
    return prompt