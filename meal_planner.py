# meal_planner.py
import json
import itertools

def load_menu_data():
    with open("menu_data.json", "r", encoding="utf-8") as f:
        return json.load(f)

def load_nutrition_data():
    with open("nutrition_data.json", "r", encoding="utf-8") as f:
        return json.load(f)

def calculate_meal_plan(user_goals, max_meals=4):
    """
    user_goals: dict with keys "carbs", "proteins", "fats", "calories"
    Returns a tuple of (selected meal items, total macros).
    """
    menu_data = load_menu_data()
    nutrition_data = load_nutrition_data()
    
    # Prepare a lower-case mapping for easier matching.
    nutrition_map = { key.lower(): value for key, value in nutrition_data.items() }
    
    available_items = []
    for item in menu_data.get("items", []):
        name = item.get("name")
        if name:
            normalized_name = name.lower()
            if normalized_name in nutrition_map:
                details = nutrition_map[normalized_name].copy()
                details["name"] = name  # preserve original formatting
                # Attach additional information from the scraped data.
                details["meal_time"] = item.get("meal_time", "Unknown")
                details["location"] = item.get("location", "Unknown")
                available_items.append(details)
    
    # Debug: print available food items and extra info.
    print("Available items for meal planning:")
    for ai in available_items:
        print(f"{ai['name']} ({ai.get('meal_time','Unknown')}, {ai.get('location','Unknown')})")
    
    if not available_items:
        return [], {"carbs": 0, "proteins": 0, "fats": 0, "calories": 0}
    
    best_combination = None
    min_diff = float("inf")
    best_total = None

    # Evaluate all combinations from 1 to max_meals items.
    for r in range(1, max_meals + 1):
        for combo in itertools.combinations(available_items, r):
            totals = {"carbs": 0, "proteins": 0, "fats": 0, "calories": 0}
            for combo_item in combo:
                for macro in totals:
                    totals[macro] += combo_item.get(macro, 0)
            # Simple sum-of-absolute differences metric.
            diff = sum(abs(totals[macro] - user_goals.get(macro, 0)) for macro in totals)
            if diff < min_diff:
                min_diff = diff
                best_combination = combo
                best_total = totals

    if best_combination is None:
        return [], {"carbs": 0, "proteins": 0, "fats": 0, "calories": 0}

    return [item for item in best_combination], best_total
