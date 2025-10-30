
from googlesearch import search
import requests
from bs4 import BeautifulSoup
import re

def fetch_search_results(query, num_results=5):
    """
    Fetch search results using googlesearch-python library.
    Returns a list of dictionaries with title, URL, and description.
    """
    try:
        results = []
        for result in search(query + " site:nseindia.com | site:moneycontrol.com | site:livemint.com", num_results=num_results, advanced=True):
            results.append({"title": result.title, "url": result.url, "description": result.description})
        print(results)
        return results
    except Exception as e:
        print(f"Error fetching search results: {e}")
        return []

def extract_stock_price(url):
    """
    Attempt to extract stock price from a financial website's HTML.
    Returns price as string or None if not found.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        page = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(page.content, 'html.parser')
        # Look for common HTML elements containing stock prices (adjust based on site structure)
        price_elements = soup.find_all(['span', 'div'], class_=re.compile('price|value|live-price|stock-price'))
        for elem in price_elements:
            text = elem.get_text().strip()
            if re.match(r'^\d+(\.\d{1,2})?$', text):  # Match numbers like 669.00 or 676
                return text
        return None
    except Exception:
        return None

def generate_response(query):
    """
    Generate a ChatGPT-like response for stock price queries.
    """
    # Assume Tata Motors if query is ambiguous
    if "tata stock" in query.lower():
        company = "Tata Motors"
        search_query = "Tata Motors stock price"
    else:
        company = query
        search_query = query + " stock price"

    results = fetch_search_results(search_query)
    
    if not results:
        return f"Sorry, I couldn't find any information for '{query}'. Please check the query or try again later!"

    # Synthesize response
    response = f"Here's what I found about the stock price of {company}:\n\n"
    price_found = False
    for i, result in enumerate(results, 1):
        price = extract_stock_price(result['url'])
        if price:
            price_found = True
            response += f"- On {result['url']}, the stock price is ₹{price}.\n"
        else:
            response += f"- {result['title']} ({result['url']}): {result['description'][:100]}...\n"

    if not price_found:
        response += "\nI couldn't extract an exact price from these sources. Try checking live prices on NSE India or Moneycontrol."
    response += f"\nWould you like me to clarify if you meant a different Tata company (e.g., Tata Steel, TCS) or dive deeper into {company}'s financials?"
    return response

if __name__ == "__main__":
    query = input("Enter your search query: ")
    print("\nGenerating response...\n")
    print(generate_response(query))