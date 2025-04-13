# scraper.py
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def scrape_menu():
    url = "https://dining.berkeley.edu/menus/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    items = []
    # Example: find elements with class "menu-item".
    # (You must adjust this selector to match the actual site structure.)
    for element in soup.find_all(class_="menu-item"):
        text = element.get_text(strip=True)
        if text:
            items.append({"name": text})
    
    menu_data = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "items": items
    }
    
    with open("menu_data.json", "w") as f:
        json.dump(menu_data, f, indent=4)
    
    return menu_data

if __name__ == "__main__":
    menu = scrape_menu()
    print(f"Scraped {len(menu['items'])} items.")
