# scraper.py
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def is_valid_food_item(text):
    """
    Return True if the text seems like a valid food item.
    Adjust the blacklist or other filtering rules as needed.
    """
    blacklist = [
        "menu", "dining", "hours", "location", "serves",
        "beverages", "contact", "find", "sustainability",
        "weekly", "news", "events"
    ]
    for word in blacklist:
        if word.lower() in text.lower():
            return False
    # Exclude excessively long strings that are likely not an individual food item.
    if len(text) > 60:
        return False
    return True

def scrape_menu():
    url = "https://dining.berkeley.edu/menus/"
    response = requests.get(url)
    
    if response.status_code != 200:
        print("Error: Could not retrieve the menu page.")
        return None
        
    soup = BeautifulSoup(response.text, "html.parser")
    food_items = []

    # --- Example approach based on assumed structure: ---
    # Assume the page is divided into blocks (divs) with class "menu-block"
    # where each block contains a header with meal time and dining hall info
    # and a list (li elements) of food items.
    blocks = soup.find_all("div", class_="menu-block")
    
    if blocks:
        for block in blocks:
            # Attempt to find a header with class "menu-title" (or adjust to match the actual page)
            header = block.find(["h2", "h3"], class_="menu-title")
            if header:
                header_text = header.get_text(strip=True)
                # If the header contains a hyphen, assume the format is "Meal Time - Dining Hall"
                if '-' in header_text:
                    parts = header_text.split('-', 1)
                    meal_time = parts[0].strip()
                    location = parts[1].strip()
                else:
                    meal_time = header_text
                    location = "Unknown"
            else:
                meal_time = "Unknown"
                location = "Unknown"
            
            # Find food items within the current block
            items = block.find_all("li")
            for li in items:
                text = li.get_text(strip=True)
                if text and is_valid_food_item(text):
                    food_items.append({
                        "name": text,
                        "meal_time": meal_time,
                        "location": location
                    })
    else:
        # Fallback: If no blocks are found, search all list items (with minimal context)
        items = soup.find_all("li")
        for li in items:
            text = li.get_text(strip=True)
            if text and is_valid_food_item(text):
                food_items.append({
                    "name": text,
                    "meal_time": "Unknown",
                    "location": "Unknown"
                })
    
    menu_data = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "items": food_items
    }
    
    with open("menu_data.json", "w", encoding="utf-8") as f:
        json.dump(menu_data, f, indent=4, ensure_ascii=False)
    
    print(f"Scraped {len(food_items)} food items.")
    return menu_data

if __name__ == "__main__":
    scrape_menu()
