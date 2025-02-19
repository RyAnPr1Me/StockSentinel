import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def get_stock_data(symbol: str, period: str = '1y') -> tuple:
    """
    Fetch stock data from Yahoo Finance
    """
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)
        info = stock.info
        return hist, info
    except Exception as e:
        raise Exception(f"Error fetching data for {symbol}: {str(e)}")

def get_stock_news(symbol: str, limit: int = 5) -> list:
    """
    Fetch recent news for the stock
    """
    try:
        stock = yf.Ticker(symbol)
        news = stock.news

        # Process and format news items
        formatted_news = []
        for item in news[:limit]:
            formatted_news.append({
                'title': item.get('title', ''),
                'publisher': item.get('publisher', ''),
                'link': item.get('link', ''),
                'published': datetime.fromtimestamp(item.get('providerPublishTime', 0)).strftime('%Y-%m-%d %H:%M'),
                'summary': item.get('summary', '')
            })
        return formatted_news
    except Exception as e:
        raise Exception(f"Error fetching news for {symbol}: {str(e)}")

def get_key_metrics(info: dict) -> dict:
    """
    Extract key financial metrics from stock info
    """
    metrics = {
        'Market Cap': info.get('marketCap', 'N/A'),
        'P/E Ratio': info.get('trailingPE', 'N/A'),
        'Forward P/E': info.get('forwardPE', 'N/A'),
        'Dividend Yield': info.get('dividendYield', 'N/A'),
        'Beta': info.get('beta', 'N/A'),
        '52 Week High': info.get('fiftyTwoWeekHigh', 'N/A'),
        '52 Week Low': info.get('fiftyTwoWeekLow', 'N/A'),
    }

    # Format metrics
    for key, value in metrics.items():
        if value != 'N/A':
            if key == 'Market Cap':
                metrics[key] = f"${value:,.0f}"
            elif key in ['Dividend Yield']:
                metrics[key] = f"{value:.2%}"
            else:
                metrics[key] = f"{value:.2f}"

    return metrics

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate technical indicators for the stock
    """
    # 20-day moving average
    df['MA20'] = df['Close'].rolling(window=20).mean()

    # 50-day moving average
    df['MA50'] = df['Close'].rolling(window=50).mean()

    # RSI (14 periods)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    return df

def analyze_portfolio(portfolio_data: pd.DataFrame) -> dict:
    """
    Analyze a portfolio of stocks
    """
    analysis = {
        'total_value': 0,
        'daily_change': 0,
        'stocks': [],
        'sector_distribution': {},
        'risk_level': 'Medium'
    }

    try:
        for _, row in portfolio_data.iterrows():
            symbol = row['Symbol']
            shares = row['Shares']

            # Get current stock data
            stock = yf.Ticker(symbol)
            current_price = stock.history(period='1d')['Close'].iloc[-1]
            prev_close = stock.history(period='2d')['Close'].iloc[-1]

            stock_value = current_price * shares
            daily_change = ((current_price - prev_close) / prev_close) * 100

            # Add to total value and daily change
            analysis['total_value'] += stock_value
            analysis['daily_change'] += (daily_change * (stock_value / analysis['total_value']))

            # Get sector information
            info = stock.info
            sector = info.get('sector', 'Unknown')
            analysis['sector_distribution'][sector] = analysis['sector_distribution'].get(sector, 0) + stock_value

            # Add stock details
            analysis['stocks'].append({
                'symbol': symbol,
                'shares': shares,
                'current_price': current_price,
                'total_value': stock_value,
                'daily_change': daily_change,
                'sector': sector
            })

        # Convert sector distribution to percentages
        for sector in analysis['sector_distribution']:
            analysis['sector_distribution'][sector] = (analysis['sector_distribution'][sector] / analysis['total_value']) * 100

        # Determine risk level based on sector diversification
        if len(analysis['sector_distribution']) < 3:
            analysis['risk_level'] = 'High'
        elif len(analysis['sector_distribution']) > 5:
            analysis['risk_level'] = 'Low'

        return analysis
    except Exception as e:
        raise Exception(f"Error analyzing portfolio: {str(e)}")