import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def create_price_chart(df: pd.DataFrame, symbol: str) -> go.Figure:
    """
    Create an interactive price chart with volume
    """
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.03, 
                        row_heights=[0.7, 0.3])

    # Candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='OHLC'
        ),
        row=1, col=1
    )

    # Add moving averages
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['MA20'],
            name='20 MA',
            line=dict(color='#e0b700')
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['MA50'],
            name='50 MA',
            line=dict(color='#ff4b4b')
        ),
        row=1, col=1
    )

    # Volume chart
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df['Volume'],
            name='Volume',
            marker_color='#304C89'
        ),
        row=2, col=1
    )

    # Update layout
    fig.update_layout(
        template='plotly_dark',
        title=f'{symbol} Stock Price',
        yaxis_title='Price',
        yaxis2_title='Volume',
        xaxis_rangeslider_visible=False,
        height=800
    )

    return fig

def create_rsi_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create RSI indicator chart
    """
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['RSI'],
            name='RSI',
            line=dict(color='#ff4b4b')
        )
    )

    # Add RSI levels
    fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5)
    fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5)

    fig.update_layout(
        template='plotly_dark',
        title='Relative Strength Index (RSI)',
        yaxis_title='RSI',
        height=300
    )

    return fig
