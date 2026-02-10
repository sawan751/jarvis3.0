# Backend/realtime_q.py
import datetime
import requests
import yfinance as yf
from newsapi import NewsApiClient
from dotenv import load_dotenv
import os

load_dotenv('api.env')
NEWS_API_KEY = os.getenv('NEWS_API_KEY')

def get_realtime_data(query: str) -> dict | None:
    query_lower = query.lower().strip()
    result = {"category": None, "key_data": None, "display_str": None}

    # ── Time / Date ───────────────────────────────────────────────
    if any(w in query_lower for w in ['time', 'clock', 'hour', 'now']):
        now = datetime.datetime.now()
        result.update({
            "category": "time",
            "key_data": now.strftime('%I:%M %p'),
            "display_str": f"Current time: {now.strftime('%I:%M %p')}"
        })
        return result

    if any(w in query_lower for w in ['date', 'today', 'day', 'tomorrow']):
        if 'tomorrow' in query_lower:
            tomorrow = datetime.date.today() + datetime.timedelta(days=1)
            disp = tomorrow.strftime('%A, %B %d, %Y')
            result.update({
                "category": "date",
                "key_data": disp,
                "display_str": f"Tomorrow is {disp}"
            })
        else:
            today = datetime.date.today()
            disp = today.strftime('%A, %B %d, %Y')
            result.update({
                "category": "date",
                "key_data": disp,
                "display_str": f"Today is {disp}"
            })
        return result

    # ── Weather (current + forecast tomorrow) ──────────────────────
    if any(w in query_lower for w in ['weather', 'temperature', 'forecast', 'climate']):
        location = "Indore"  # default
        if 'in' in query_lower:
            parts = query_lower.split('in')
            if len(parts) > 1:
                location = parts[1].strip().title()

        forecast_day = "today" if 'today' in query_lower or 'current' in query_lower else "tomorrow" if 'tomorrow' in query_lower else "today"

        try:
            # wttr.in format=3 is current; use %l for location + %c %t for condition/temp
            url = f'https://wttr.in/{location}?format="%l:+%c+%t"'
            resp = requests.get(url, timeout=6)
            if resp.status_code == 200:
                data = resp.text.strip().strip('"')
                result.update({
                    "category": "weather",
                    "key_data": data,
                    "display_str": f"{forecast_day.capitalize()} weather in {location}: {data}"
                })
                return result
        except Exception as e:
            print(f"Weather fetch failed: {e}")

    # ── Stock — better company name parsing ────────────────────────
    if any(w in query_lower for w in ['stock', 'price', 'share', 'nse', 'bse']):
        # Simple mapping for common Tata companies
        company_map = {
            'tata': 'TATAMOTORS.NS',      # Tata Motors
            'tcs': 'TCS.NS',              # Tata Consultancy
            'tatamotors': 'TATAMOTORS.NS',
            'tataconsultancy': 'TCS.NS',
            'reliance': 'RELIANCE.NS'
        }

        symbol = "RELIANCE.NS"  # fallback
        words = query_lower.split()
        for word in words:
            if word in company_map:
                symbol = company_map[word]
                break
            # Fallback: take uppercase word as ticker
            if word.isupper() and 3 <= len(word) <= 8:
                symbol = word.upper() + ".NS"
                break

        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            price = info.get('currentPrice') or info.get('regularMarketPrice', 'N/A')
            company_name = info.get('shortName', symbol.replace('.NS', ''))
            result.update({
                "category": "stock",
                "key_data": {"symbol": symbol, "price": price},
                "display_str": f"Current price of {company_name} ({symbol}): ₹{price}"
            })
            return result
        except Exception as e:
            print(f"Stock fetch failed: {e}")

    # ── News ───────────────────────────────────────────────────────
    if any(w in query_lower for w in ['news', 'headline', 'latest', 'breaking', "today's news"]):
        if not NEWS_API_KEY:
            return None
        try:
            newsapi = NewsApiClient(api_key=NEWS_API_KEY)
            headlines = newsapi.get_top_headlines(language='en', country='in', page_size=4)
            articles = headlines.get('articles', [])
            if articles:
                top_news = [f"{a['title']} — {a['source']['name']}" for a in articles[:3]]
                result.update({
                    "category": "news",
                    "key_data": top_news,
                    "display_str": "Top headlines in India right now:\n" + "\n".join(top_news)
                })
                return result
        except Exception as e:
            print(f"News fetch failed: {e}")

    return None