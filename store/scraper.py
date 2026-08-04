import requests
from bs4 import BeautifulSoup

def scrape_product_data(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = response.apparent_encoding
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Generic or Books to Scrape compatible selectors
        title_elem = soup.find('h1') or soup.find('title')
        title = title_elem.get_text(strip=True) if title_elem else "Untitled Product"
        
        # Price extraction logic
        price_elem = soup.find('p', class_='price_color') or soup.find(class_='price')
        raw_price = price_elem.get_text(strip=True) if price_elem else "0"
        
        # Clean price to keep only numbers and decimal
        import re
        price_numbers = re.findall(r"[\d\.]+", raw_price)
        price = float(price_numbers[0]) if price_numbers else 0.0

        # Image extraction
        img_elem = soup.find('img')
        image_url = img_elem.get('src', '') if img_elem else ''

        return {
            "success": True,
            "title": title,
            "price": price,
            "image_url": image_url,
            "url": url
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }