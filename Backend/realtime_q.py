import datetime
import requests
import yfinance as yf
from newsapi import NewsApiClient
from dotenv import load_dotenv
import os

def realtime(user_input):
    load_dotenv('api.env')
    api_key = os.getenv('NEWS_API_KEY')
    """
    Handle realtime queries with actual data.
    """
    query_lower = user_input.lower()

    if 'time' in query_lower:
        now = datetime.datetime.now()
        return f"The current time is {now.strftime('%I:%M %p')}."

    elif 'date' in query_lower:
        today = datetime.date.today()
        return f"Today's date is {today.strftime('%A, %B %d, %Y')}."

    elif 'weather' in query_lower or 'temperature' in query_lower or 'forecast' in query_lower:
        try:
            location = "Indore"  # Default, can parse from query
            if 'in' in query_lower:
                # Simple parse, e.g., weather in London
                parts = query_lower.split('in')
                if len(parts) > 1:
                    location = parts[1].strip()
            response = requests.get(f'https://wttr.in/{location}?format=3')
            if response.status_code == 200:
                return f"Weather in {location}: {response.text.strip()}"
            else:
                return "Unable to fetch weather data."
        except Exception as e:
            return f"Error fetching weather: {e}"

    elif 'stock' in query_lower or 'price' in query_lower:
        try:
            # Extract stock symbol, assume like "AAPL stock price"
            symbol = "AAPL"  # Default
            words = query_lower.split()
            for word in words:
                if word.isupper() and len(word) <= 5:  # Simple check for ticker
                    symbol = word.upper()
                    break
            stock = yf.Ticker(symbol)
            info = stock.info
            price = info.get('currentPrice', 'N/A')
            return f"The current price of {symbol} is ${price}."
        except Exception as e:
            return f"Error fetching stock price: {e}"

    elif 'news' in query_lower or 'latest' in query_lower:
        try:
            # Use NewsAPI, assume API key in env
            if api_key:
                newsapi = NewsApiClient(api_key=api_key)
                top_headlines = newsapi.get_top_headlines(language='en', country='us')
                articles = top_headlines['articles'][:3]  # Top 3
                news = [f"{art['title']} - {art['source']['name']}" for art in articles]
                return "Latest news: " + "; ".join(news)
            else:
                return "News API key not set."
        except Exception as e:
            return f"Error fetching news: {e}"

    else:
        return None