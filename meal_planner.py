# meal_planner.py
import json
import itertools

def load_menu_data():
    with open("menu_data.json", "r") as f:
        return json.load(f)

def load_nutrition_data():
    with open("nutrition_data.json", "r") as f:
        return json.load(f)

def calculate_meal_plan(user_goals, max_meals=4, top_n=3):
    """
    user_goals: dict with keys "carbs", "proteins", "fats", "calories"
    Returns a list of up to top_n suggestions.
    Each suggestion is a dict with:
      - "meals": list of meal items (each with nutritional info)
      - "total": combined macros totals
      - "diff": the sum-of-absolute-differences between the combo totals and the user goals.
    """
    menu_data = load_menu_data()
    nutrition_data = load_nutrition_data()
    
    # Create a mapping with lower-case keys for matching.
    nutrition_map = { key.lower(): value for key, value in nutrition_data.items() }
    
    available_items = []
    for item in menu_data.get("items", []):
        name = item.get("name")
        if name:
            normalized_name = name.lower()
            if normalized_name in nutrition_map:
                details = nutrition_map[normalized_name].copy()
                details["name"] = name  # Preserve original formatting
                available_items.append(details)
    
    if not available_items:
        return []
    
    suggestions = []
    # Evaluate all combinations with 1 to max_meals items.
    for r in range(1, max_meals + 1):
        for combo in itertools.combinations(available_items, r):
            totals = {"carbs": 0, "proteins": 0, "fats": 0, "calories": 0}
            for item in combo:
                for macro in totals:
                    totals[macro] += item.get(macro, 0)
            # Simple measure: sum of absolute differences between totals and user goals.
            diff = sum(abs(totals[macro] - user_goals.get(macro, 0)) for macro in totals)
            suggestions.append({
                "meals": [item for item in combo],
                "total": totals,
                "diff": diff
            })
    
    # Sort suggestions by how close they are (lower diff is better)
    suggestions.sort(key=lambda x: x["diff"])
    
    return suggestions[:top_n]

# For testing via command line
if __name__ == "__main__":
    sample_goals = {"carbs": 300, "proteins": 100, "fats": 70, "calories": 2000}
    suggestions = calculate_meal_plan(sample_goals)
    for idx, suggestion in enumerate(suggestions, start=1):
        print(f"Option {idx}:")
        for meal in suggestion["meals"]:
            print(f" - {meal['name']}: Carbs {meal.get('carbs')}, Proteins {meal.get('proteins')}, Fats {meal.get('fats')}, Calories {meal.get('calories')}")
        print("Totals:", suggestion["total"])
        print("Diff:", suggestion["diff"])
        print("-----")
