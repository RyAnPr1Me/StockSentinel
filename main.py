import streamlit as st
import pandas as pd
from utils.data_fetcher import (
    get_stock_data, get_key_metrics, calculate_technical_indicators,
    get_stock_news, analyze_portfolio
)
from utils.chart_helper import create_price_chart, create_rsi_chart
from utils.ai_analyzer import get_stock_analysis

# Page configuration
st.set_page_config(
    page_title="Stock Analysis Tool",
    page_icon="📈",
    layout="wide"
)

# Load custom CSS
with open('.streamlit/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Home"
if 'analysis_symbol' not in st.session_state:
    st.session_state.analysis_symbol = ""

# Sidebar navigation
page = st.sidebar.radio("Navigate", ["Home", "Stock Analysis", "Portfolio Analysis"],
                       key="navigation",
                       index=["Home", "Stock Analysis", "Portfolio Analysis"].index(st.session_state.current_page))

# Update current page
st.session_state.current_page = page

# Metric explanations
metric_explanations = {
    'Market Cap': "Total value of a company's shares. Higher market cap typically indicates a more stable company.",
    'P/E Ratio': "Price-to-Earnings ratio compares stock price to earnings per share. Lower P/E might indicate an undervalued stock.",
    'Forward P/E': "P/E ratio using projected earnings. Helps assess future growth expectations.",
    'Dividend Yield': "Annual dividend payments relative to stock price. Higher yield means better income potential.",
    'Beta': "Measure of stock's volatility compared to the market. Beta > 1 means more volatile than market.",
    '52 Week High': "Highest price in the past year. Helps understand price range and momentum.",
    '52 Week Low': "Lowest price in the past year. Helps understand price range and support levels."
}

if page == "Home":
    # Landing page content remains unchanged
    st.markdown('<div class="landing-container">', unsafe_allow_html=True)
    st.title("📈 Welcome to Stock Analysis Tool")
    st.markdown("""
    Your comprehensive platform for stock market analysis and portfolio management.

    ### Features:
    - 📊 Real-time stock data and interactive charts
    - 🔍 Detailed technical and fundamental analysis
    - 📰 Latest market news and updates
    - 📱 Portfolio tracking and analysis

    ### Getting Started:
    1. Enter a stock symbol (e.g., AAPL for Apple Inc.)
    2. View detailed analysis and metrics
    3. Upload your portfolio for comprehensive insights
    """)

    # Quick analysis section
    st.markdown("### Quick Stock Analysis")
    symbol = st.text_input("Enter Stock Symbol (e.g., AAPL, GOOGL)").upper()
    if st.button("Analyze"):
        st.session_state.analysis_symbol = symbol
        st.session_state.current_page = "Stock Analysis"
        st.experimental_rerun()

    st.markdown('</div>', unsafe_allow_html=True)

elif page == "Stock Analysis":
    # Stock Analysis page content remains unchanged
    try:
        st.title("📈 Stock Analysis")

        col1, col2 = st.columns([2, 1])
        with col1:
            symbol = st.text_input("Enter Stock Symbol (e.g., AAPL, GOOGL)",
                                 value=st.session_state.analysis_symbol).upper()
        with col2:
            period = st.selectbox("Select Time Period",
                                options=['1mo', '3mo', '6mo', '1y', '2y', '5y'],
                                index=3)

        if symbol:
            with st.spinner('Fetching stock data...'):
                hist_data, stock_info = get_stock_data(symbol, period)
                news_items = get_stock_news(symbol)

            if hist_data.empty:
                st.error("No data found for the given symbol")
            else:
                df = calculate_technical_indicators(hist_data)

                st.header(f"{stock_info.get('longName', symbol)}")
                st.markdown(f"**Sector:** {stock_info.get('sector', 'N/A')} | **Industry:** {stock_info.get('industry', 'N/A')}")

                current_price = df['Close'].iloc[-1]
                price_change = df['Close'].iloc[-1] - df['Close'].iloc[-2]
                price_change_pct = (price_change / df['Close'].iloc[-2]) * 100

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Current Price", f"${current_price:.2f}", f"{price_change_pct:.2f}%")

                st.subheader("Key Metrics")
                metrics = get_key_metrics(stock_info)

                metric_cols = st.columns(3)
                for i, (metric, value) in enumerate(metrics.items()):
                    with metric_cols[i % 3]:
                        st.markdown(f'<div class="metric-card">', unsafe_allow_html=True)
                        st.metric(metric, value)
                        st.markdown(f'<div class="metric-explanation">{metric_explanations[metric]}</div>',
                                      unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                st.subheader("Price Chart")
                price_chart = create_price_chart(df, symbol)
                st.plotly_chart(price_chart, use_container_width=True)

                st.subheader("Technical Indicators")
                rsi_chart = create_rsi_chart(df)
                st.plotly_chart(rsi_chart, use_container_width=True)

                st.subheader("📰 Latest News")
                for news in news_items:
                    st.markdown(f'<div class="news-card">', unsafe_allow_html=True)
                    st.markdown(f"### {news['title']}")
                    st.markdown(f"**Published:** {news['published']} | **Source:** {news['publisher']}")
                    st.markdown(news['summary'])
                    st.markdown(f"[Read more]({news['link']})")
                    st.markdown('</div>', unsafe_allow_html=True)

                st.subheader("🤖 Analysis Insights")
                analysis = get_stock_analysis(df, metrics, stock_info)

                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"### Summary\n{analysis['summary']}")
                    st.markdown(f"### Technical Analysis\n{analysis['technical_analysis']}")

                with col2:
                    st.markdown(f'<div class="recommendation-card">', unsafe_allow_html=True)
                    st.markdown(f"### Recommendation: {analysis['recommendation']}")
                    st.markdown(f"**Risk Level:** {analysis['risk_level']}")
                    st.markdown(f"_{analysis.get('reasoning', '')}_")
                    st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.info("Please check the stock symbol and try again")

else:  # Portfolio Analysis page
    st.title("📊 Portfolio Analysis")
    st.markdown("""
    Upload your portfolio CSV file to get a comprehensive analysis of your investments.

    The CSV file should include:
    - **Symbol**: Stock symbol (e.g., AAPL)
    - **Shares**: Number of shares owned

    Click the button below to download a sample CSV template:
    """)

    # Create sample DataFrame
    sample_df = pd.DataFrame({
        'Symbol': ['AAPL', 'GOOGL', 'MSFT'],
        'Shares': [10, 5, 15]
    })

    # Convert DataFrame to CSV string
    csv_string = sample_df.to_csv(index=False)

    # Download button with proper MIME type
    st.download_button(
        label="⬇️ Download Sample CSV Template",
        data=csv_string,
        file_name="portfolio_template.csv",
        mime="text/csv",
        key="download_sample"
    )

    # File upload
    uploaded_file = st.file_uploader("Upload Portfolio CSV", type=['csv'])

    if uploaded_file is not None:
        try:
            portfolio_df = pd.read_csv(uploaded_file)
            required_columns = ['Symbol', 'Shares']

            if not all(col in portfolio_df.columns for col in required_columns):
                st.error("CSV must contain 'Symbol' and 'Shares' columns")
            else:
                with st.spinner('Analyzing portfolio...'):
                    analysis = analyze_portfolio(portfolio_df)

                st.subheader("Portfolio Overview")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Value", f"${analysis['total_value']:,.2f}")
                with col2:
                    st.metric("Daily Change", f"{analysis['daily_change']:.2f}%")
                with col3:
                    st.metric("Risk Level", analysis['risk_level'])

                st.subheader("Sector Distribution")
                sector_df = pd.DataFrame([
                    {"Sector": k, "Percentage": v}
                    for k, v in analysis['sector_distribution'].items()
                ])
                st.bar_chart(sector_df.set_index('Sector'))

                st.subheader("Stock Details")
                for stock in analysis['stocks']:
                    with st.expander(f"{stock['symbol']} - {stock['shares']} shares"):
                        cols = st.columns(3)
                        cols[0].metric("Current Price", f"${stock['current_price']:.2f}")
                        cols[1].metric("Total Value", f"${stock['total_value']:,.2f}")
                        cols[2].metric("Daily Change", f"{stock['daily_change']:.2f}%")

        except Exception as e:
            st.error(f"Error analyzing portfolio: {str(e)}")
            st.info("Please make sure your CSV file is properly formatted")

# Footer
st.markdown("---")
st.markdown("Data provided by Yahoo Finance")