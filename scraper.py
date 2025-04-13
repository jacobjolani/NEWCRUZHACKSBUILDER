# scraper.py
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def is_valid_food_item(text):
    """
    Return True if the text seems like a valid food item.
    You can modify the blacklist or add more filtering conditions as needed.
    """
    blacklist = [
        "menu", "dining", "hours", "location", "serves", "beverages",
        "contact", "find", "sustainability", "weekly", "news", "events"
    ]
    # Exclude if any blacklist word appears (case-insensitive)
    for word in blacklist:
        if word.lower() in text.lower():
            return False
    # Exclude overly long items that are likely not individual food items.
    if len(text) > 60:
        return False
    return True

def scrape_menu():
    url = "https://dining.berkeley.edu/menus/"
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code != 200:
        print("Error: Could not retrieve the menu page.")
        return None
        
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Initialize an empty list to hold valid food items.
    food_items = []
    
    # Try to narrow down the search by finding a specific container.
    # Inspect the page (right-click -> "View page source" or "Inspect Element")
    # and change "menu-content" to a container that wraps only the food menu listings.
    container = soup.find("div", class_="menu-content")
    
    if container:
        # Assume that within this container the food items are in list items (li tags)
        items = container.find_all("li")
    else:
        # If a specific container is not found, fallback to finding all list items.
        items = soup.find_all("li")
    
    # Loop through each found item and filter by our criteria.
    for item in items:
        text = item.get_text(strip=True)
        if text and is_valid_food_item(text):
            food_items.append({"name": text})
    
    # In case the container-based search returned nothing or too little,
    # you may extend the search to also look for other containers.
    # For example, look for items inside div tags with a common class used for food items.
    if not food_items:
        alternative_items = soup.find_all("div", class_="menu-item")
        for div in alternative_items:
            text = div.get_text(strip=True)
            if text and is_valid_food_item(text):
                food_items.append({"name": text})
    
    # Create the final menu data structure.
    menu_data = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "items": food_items
    }
    
    # Save the filtered food items into menu_data.json.
    with open("menu_data.json", "w", encoding="utf-8") as f:
        json.dump(menu_data, f, indent=4, ensure_ascii=False)
    
    print(f"Scraped {len(food_items)} food items.")
    return menu_data

if __name__ == "__main__":
    scrape_menu()
