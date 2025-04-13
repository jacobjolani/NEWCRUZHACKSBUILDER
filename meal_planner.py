# meal_planner.py
import json
import itertools

def load_nutrition_data():
    with open("nutrition_data.json", "r") as f:
        return json.load(f)

def calculate_meal_plans(user_goals, max_meals=4, top_n=10):
    """
    user_goals: dictionary with numeric keys "calories", "fats", "carbs", "proteins"
    max_meals: maximum number of food items to include in a combination
    top_n: number of best combinations (sorted by overall difference) to return
    
    Returns a list of candidate meal plans, each with:
      - "combo": list of selected food items
      - "totals": dictionary of total macros in that combo
      - "diff": numeric value (sum of absolute differences from targets)
    """
    nutrition_data = load_nutrition_data()
    
    # Build a list of food items from nutrition_data.
    available_items = []
    for key, nutrition in nutrition_data.items():
        try:
            # Convert macros to float values (or leave them as numbers)
            calories = float(nutrition.get("calories", 0))
            fats     = float(nutrition.get("fats", 0))
            carbs    = float(nutrition.get("carbs", 0))
            proteins = float(nutrition.get("proteins", 0))
        except Exception as e:
            print(f"Error converting nutrition for {key}: {e}")
            continue
        
        available_items.append({
            "name": key,
            "calories": calories,
            "fats": fats,
            "carbs": carbs,
            "proteins": proteins
        })
    
    if not available_items:
        return []
    
    candidate_plans = []
    
    # Iterate over combinations from 1 to max_meals items
    for r in range(1, max_meals + 1):
        for combo in itertools.combinations(available_items, r):
            totals = {"calories": 0, "fats": 0, "carbs": 0, "proteins": 0}
            for item in combo:
                totals["calories"] += item["calories"]
                totals["fats"]     += item["fats"]
                totals["carbs"]    += item["carbs"]
                totals["proteins"] += item["proteins"]
            # Compute total absolute deviation from user goals:
            diff = (
                abs(totals["calories"] - user_goals.get("calories", 0)) +
                abs(totals["fats"]     - user_goals.get("fats", 0)) +
                abs(totals["carbs"]    - user_goals.get("carbs", 0)) +
                abs(totals["proteins"] - user_goals.get("proteins", 0))
            )
            candidate_plans.append({"combo": [item for item in combo], "totals": totals, "diff": diff})
    
    # Sort the candidate plans by diff (lower diff is better)
    candidate_plans.sort(key=lambda x: x["diff"])
    
    # Return the top N results (or all if fewer than top_n)
    return candidate_plans[:top_n]

# For testing when running standalone:
if __name__ == "__main__":
    sample_goals = {
        "calories": 2000,
        "fats": 70,
        "carbs": 250,
        "proteins": 150
    }
    plans = calculate_meal_plans(sample_goals, max_meals=4, top_n=10)
    if plans:
        for idx, plan in enumerate(plans, start=1):
            print(f"Plan {idx}: Diff = {plan['diff']}")
            for item in plan["combo"]:
                print(f"  - {item['name']}: Calories {item['calories']}, Fats {item['fats']}, Carbs {item['carbs']}, Proteins {item['proteins']}")
            print("  Totals:", plan["totals"])
            print("-" * 40)
    else:
        print("No candidate plans found.")
