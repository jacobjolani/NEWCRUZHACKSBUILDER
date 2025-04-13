# meal_planner.py
import json
import itertools

def load_nutrition_data():
    with open("nutrition_data.json", "r") as f:
        return json.load(f)

def calculate_meal_plan(user_goals, max_meals=4):
    """
    user_goals: dictionary with keys "calories", "fats", "carbs", "proteins" (all numeric)
    max_meals: maximum number of food items to combine in a plan.
    
    Returns a tuple: (list of selected food items, total macros dictionary)
    
    This version uses the entire list of foods from nutrition_data.json.
    """
    nutrition_data = load_nutrition_data()
    
    # Create a list of available food items from the entire nutrition database.
    # Convert numeric values from strings to floats if necessary.
    available_items = []
    for key, nutrition in nutrition_data.items():
        # Convert values to floats (if they are not already numeric)
        try:
            calories = float(nutrition.get("calories", 0))
            fats = float(nutrition.get("fats", 0))
            carbs = float(nutrition.get("carbs", 0))
            proteins = float(nutrition.get("proteins", 0))
        except Exception as e:
            print(f"Error converting nutrition for {key}: {e}")
            continue
        
        item = {
            "name": key,
            "calories": calories,
            "fats": fats,
            "carbs": carbs,
            "proteins": proteins
        }
        available_items.append(item)

    if not available_items:
        return [], {"calories": 0, "fats": 0, "carbs": 0, "proteins": 0}

    best_combination = None
    min_diff = float("inf")
    best_total = None

    # Try every combination from 1 to max_meals items:
    for r in range(1, max_meals + 1):
        for combo in itertools.combinations(available_items, r):
            totals = {"calories": 0, "fats": 0, "carbs": 0, "proteins": 0}
            for item in combo:
                totals["calories"] += item["calories"]
                totals["fats"] += item["fats"]
                totals["carbs"] += item["carbs"]
                totals["proteins"] += item["proteins"]
            
            # Calculate a simple difference metric: sum of absolute differences.
            diff = (abs(totals["calories"] - user_goals.get("calories", 0)) +
                    abs(totals["fats"] - user_goals.get("fats", 0)) +
                    abs(totals["carbs"] - user_goals.get("carbs", 0)) +
                    abs(totals["proteins"] - user_goals.get("proteins", 0)))
            
            if diff < min_diff:
                min_diff = diff
                best_combination = combo
                best_total = totals

    if best_combination is None:
        return [], {"calories": 0, "fats": 0, "carbs": 0, "proteins": 0}

    # Return the best combination as a list and the corresponding totals.
    return [item for item in best_combination], best_total

# Example testing when run standalone:
if __name__ == "__main__":
    sample_goals = {
        "calories": 2000,
        "fats": 70,
        "carbs": 250,
        "proteins": 150
    }
    meals, totals = calculate_meal_plan(sample_goals, max_meals=4)
    print("Suggested Meals:")
    for meal in meals:
        print(f"- {meal['name']}: Calories: {meal['calories']}, Fats: {meal['fats']}, Carbs: {meal['carbs']}, Proteins: {meal['proteins']}")
    print("Total macros:", totals)
