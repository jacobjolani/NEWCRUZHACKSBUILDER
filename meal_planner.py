# meal_planner.py
import json
import itertools

def load_menu_data():
    with open("menu_data.json", "r") as f:
        return json.load(f)

def load_nutrition_data():
    with open("nutrition_data.json", "r") as f:
        return json.load(f)

def calculate_meal_plan(user_goals, max_meals=4):
    """
    user_goals: dict with keys "carbs", "proteins", "fats", "calories"
    Returns a tuple: (list of selected meal items, total macros dictionary)
    """
    menu_data = load_menu_data()
    nutrition_data = load_nutrition_data()
    
    available_items = []
    for item in menu_data.get("items", []):
        name = item.get("name")
        if name in nutrition_data:
            # Make a copy of the nutritional info and add the name.
            details = nutrition_data[name].copy()
            details["name"] = name
            available_items.append(details)
    
    # If no items are matched, return empty plan.
    if not available_items:
        return [], {"carbs": 0, "proteins": 0, "fats": 0, "calories": 0}
    
    best_combination = None
    min_diff = float("inf")
    best_total = None

    # Check combinations from 1 to max_meals
    for r in range(1, max_meals + 1):
        for combo in itertools.combinations(available_items, r):
            totals = {"carbs": 0, "proteins": 0, "fats": 0, "calories": 0}
            for item in combo:
                for macro in totals:
                    totals[macro] += item.get(macro, 0)
            # Calculate a simple difference (sum of absolute differences)
            diff = sum(abs(totals[macro] - user_goals.get(macro, 0)) for macro in totals)
            if diff < min_diff:
                min_diff = diff
                best_combination = combo
                best_total = totals
                
    if best_combination is None:
        return [], {"carbs": 0, "proteins": 0, "fats": 0, "calories": 0}
    
    # Convert the best combination from tuple to list for easier handling.
    return [item for item in best_combination], best_total
