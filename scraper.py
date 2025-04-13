# scraper.py
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def is_valid_food_item(text):
    """
    Determines if text is likely an actual food item.
    Adjust the blacklist words and length limits as needed.
    """
    blacklist = [
        "menu", "dining", "hours", "location", "serves",
        "beverages", "contact", "sustainability", "news", "events",
        "allergen", "nutrient", "calories", "ingredients"  # add words that indicate header or info
    ]
    # Exclude empty or very short strings
    if not text or len(text) < 3:
        return False
    # Exclude strings that are too long (these might be descriptions or headers)
    if len(text) > 60:
        return False
    # Exclude strings containing any blacklisted word (case-insensitive)
    lower_text = text.lower()
    for word in blacklist:
        if word in lower_text:
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
    
    # --- Attempt 1: Look for grouped dining hall blocks ---
    # Many dining sites group menus by dining hall and then by meal (e.g. brunch, dinner).
    # This example looks for a container with a class like "dining-hall".
    # Adjust the class names below (e.g., "dining-hall", "meal-section") according to the actual structure.
    dining_hall_blocks = soup.find_all("div", class_="dining-hall")
    
    if dining_hall_blocks:
        for hall in dining_hall_blocks:
            # Try to extract the dining hall name from a header (e.g., h2)
            hall_header = hall.find("h2")
            location = hall_header.get_text(strip=True) if hall_header else "Unknown"
            
            # Within each dining hall block, look for meal sections
            meal_sections = hall.find_all("div", class_="meal-section")
            for section in meal_sections:
                # Try to extract the meal time (for example, from an h3 tag)
                meal_header = section.find("h3")
                meal_time = meal_header.get_text(strip=True) if meal_header else "Unknown"
                
                # Find food items. They might be listed as <li> items.
                items = section.find_all("li")
                for li in items:
                    text = li.get_text(strip=True)
                    if text and is_valid_food_item(text):
                        food_items.append({
                            "name": text,
                            "meal_time": meal_time,
                            "location": location
                        })
    else:
        # --- Fallback Approach ---
        # If the expected grouping is not found, use a generic approach.
        # For example, look for all elements with a class "menu-item"
        for element in soup.find_all(class_="menu-item"):
            text = element.get_text(strip=True)
            if text and is_valid_food_item(text):
                food_items.append({
                    "name": text,
                    "meal_time": "Unknown",
                    "location": "Unknown"
                })
    
    # Build the final menu data with the current date
    menu_data = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "items": food_items
    }
    
    # Save the filtered food items to menu_data.json
    with open("menu_data.json", "w", encoding="utf-8") as f:
        json.dump(menu_data, f, indent=4, ensure_ascii=False)
    
    print(f"Scraped {len(food_items)} food items.")
    return menu_data

if __name__ == "__main__":
    scrape_menu()
