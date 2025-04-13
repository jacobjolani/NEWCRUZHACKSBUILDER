# meal_planner.py
import json
import pulp

def load_nutrition_data():
    with open("nutrition_data.json", "r") as f:
        return json.load(f)

def calculate_meal_plan(user_goals):
    """
    user_goals: dictionary with numeric keys "calories", "fats", "carbs", "proteins"
    Returns a tuple: (list of selected food items, total macros dictionary)
    
    This version uses a mixed-integer linear programming formulation via PuLP.
    """
    nutrition_data = load_nutrition_data()
    
    # Build the list of available food items from the entire nutrition database.
    items = []
    for key, nutrition in nutrition_data.items():
        try:
            calories = float(nutrition.get("calories", 0))
            fats     = float(nutrition.get("fats", 0))
            carbs    = float(nutrition.get("carbs", 0))
            proteins = float(nutrition.get("proteins", 0))
        except Exception as e:
            print(f"Error converting nutrition for {key}: {e}")
            continue
        
        items.append({
            "name": key,
            "calories": calories,
            "fats": fats,
            "carbs": carbs,
            "proteins": proteins
        })

    if not items:
        return [], {"calories": 0, "fats": 0, "carbs": 0, "proteins": 0}
        
    # Create a linear programming problem to minimize total deviation from targets.
    prob = pulp.LpProblem("MealPlanner", pulp.LpMinimize)
    
    n = len(items)
    # Decision variables: x[i] = 1 if item i is selected, else 0.
    x = pulp.LpVariable.dicts("select", range(n), cat="Binary")
    
    # Macros we care about:
    macros = ["calories", "fats", "carbs", "proteins"]
    
    # Slack variables for absolute differences for each macro:
    over = {}   # amount above the target
    under = {}  # amount below the target
    for m in macros:
        over[m]  = pulp.LpVariable(f"over_{m}", lowBound=0, cat="Continuous")
        under[m] = pulp.LpVariable(f"under_{m}", lowBound=0, cat="Continuous")
    
    # Constraints: for each macro, the selected items' total minus the target equals (over - under)
    for m in macros:
        prob += (pulp.lpSum([x[i] * items[i][m] for i in range(n)]) - user_goals.get(m, 0) ==
                 over[m] - under[m]), f"balance_{m}"
    
    # (Optional) You may also want to set a maximum number of items if desired.
    # For example, uncomment the following lines to limit selection to, say, 6 items:
    # max_items = 6
    # prob += pulp.lpSum([x[i] for i in range(n)]) <= max_items, "max_items"
    
    # Objective: minimize the total absolute deviation
    prob += pulp.lpSum([over[m] + under[m] for m in macros]), "TotalDeviation"
    
    # Solve the integer linear program
    prob.solve()
    
    if pulp.LpStatus[prob.status] != "Optimal":
        print("No optimal solution found!")
        return [], {m: 0 for m in macros}
    
    # Retrieve selected items
    selected_items = []
    for i in range(n):
        if pulp.value(x[i]) == 1:
            selected_items.append(items[i])
    
    # Calculate totals for the combination
    totals = {m: sum(item[m] for item in selected_items) for m in macros}
    
    return selected_items, totals

# For testing when run as a script:
if __name__ == "__main__":
    sample_goals = {
        "calories": 2000,
        "fats": 70,
        "carbs": 250,
        "proteins": 150
    }
    meals, totals = calculate_meal_plan(sample_goals)
    print("Selected meals:")
    for meal in meals:
        print(f"- {meal['name']}: Calories: {meal['calories']}, Fats: {meal['fats']}, Carbs: {meal['carbs']}, Proteins: {meal['proteins']}")
    print("Total macros:", totals)
