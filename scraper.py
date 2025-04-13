# scraper.py
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import pickle
import numpy as np

# Load vectorizer & classifier
with open("food_classifier.pkl", "rb") as f:
    vectorizer, clf = pickle.load(f)

def is_food_item_ml(text, threshold=0.8):
    """
    Use the trained ML classifier to decide if text is a food item.
    Returns True if predicted probability of "food" exceeds the threshold.
    """
    X_vec = vectorizer.transform([text])
    # The classifier returns [prob_not_food, prob_food] if we do predict_proba
    proba = clf.predict_proba(X_vec)[0]
    
    # 'food' is presumably the second class if the classes_ are in alphabetical order
    # Let's figure out which index is "food" by searching clf.classes_:
    # e.g. clf.classes_ -> ['food', 'not_food'] or vice versa
    try:
        idx_food = list(clf.classes_).index("food")
    except ValueError:
        # fallback if order is reversed
        idx_food = 1

    return proba[idx_food] >= threshold

def scrape_menu():
    """
    Scrape the UC Berkeley Dining site and filter results using the classifier.
    """
    url = "https://dining.berkeley.edu/menus/"
    response = requests.get(url)
    
    if response.status_code != 200:
        print("Error: Could not retrieve the menu page.")
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Collect items (this may need adjusting based on the site structure)
    # For example, many menus have 'menu-item' class or <li> tags inside certain containers
    # The user’s screenshot suggests multiple dining halls, each with a label or block
    # We can try a broad approach: find all <li> and handle them
    all_items = soup.find_all("li")
    
    # We’ll track both text (food name) and possibly meal/hall if available
    # But for simplicity, let's just store the text
    filtered_items = []
    for li in all_items:
        text = li.get_text(strip=True)
        if text:
            # Classify with ML
            if is_food_item_ml(text):
                # Attempt to parse meal/hall from parent elements, if needed
                # e.g., location = find_location(li)
                # But in this minimal example, we just store text
                filtered_items.append({
                    "name": text,
                    "meal_time": "Unknown",
                    "location": "Unknown"
                })
    
    # Build final JSON
    menu_data = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "items": filtered_items
    }
    
    # Save to menu_data.json
    with open("menu_data.json", "w", encoding="utf-8") as f:
        json.dump(menu_data, f, indent=4, ensure_ascii=False)
    
    print(f"Scraped {len(filtered_items)} likely food items.")
    return menu_data

if __name__ == "__main__":
    data = scrape_menu()
