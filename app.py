import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime
import serpapi
from serpapi import GoogleSearch

st.set_page_config(page_title="Sentiment Alert Tracker", layout="centered")

st.title("🚨 Sentiment Alert Tracker")

st.markdown("""
Monitor sentiment spikes from Reddit and Google News about **stocks** or **crypto**, using SerpAPI.

Enter a keyword like `Bitcoin`, `TSLA`, or `AAPL`.
""")

SERPAPI_API_KEY = st.secrets.get("SERPAPI_API_KEY", "")

query = st.text_input("🔍 Enter a stock or crypto keyword", "Bitcoin")

if query and SERPAPI_API_KEY:
    def fetch_news_results(query):
        params = {
            "engine": "google_news",
            "q": query,
            "api_key": SERPAPI_API_KEY,
            "num": "20"
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        news_results = results.get("news_results", [])
        return news_results

    def analyze_sentiment(text):
        text = text.lower()
        if any(word in text for word in ["soars", "surges", "rises", "up", "gains", "bullish"]):
            return 1
        elif any(word in text for word in ["plunges", "falls", "drops", "down", "bearish"]):
            return -1
        return 0

    sentiment_data = []
    raw_news = fetch_news_results(query)

    for item in raw_news:
        sentiment = analyze_sentiment(item.get("title", ""))
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sentiment_data.append({"time": timestamp, "sentiment": sentiment, "title": item.get("title", "")})

    df = pd.DataFrame(sentiment_data)

    if not df.empty:
        st.subheader(f"📈 Sentiment Trend for '{query}'")
        st.line_chart(df["sentiment"])

        if df["sentiment"].sum() > 5:
            st.success("🔔 Positive sentiment spike detected!")
        elif df["sentiment"].sum() < -5:
            st.error("🔔 Negative sentiment spike detected!")

        with st.expander("📰 Headlines"):
            for row in df.itertuples():
                st.write(f"- {row.title}")

else:
    st.warning("Please enter a keyword and ensure your SerpAPI key is set in Streamlit Secrets.")
