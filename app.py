# app.py
from flask import Flask, render_template, request, jsonify
from meal_planner import calculate_meal_plans
import scraper

app = Flask(__name__)

# Home route serves the HTML page.
@app.route('/')
def index():
    return render_template('index.html')

# Optional endpoint to manually trigger a menu scrape.
@app.route('/scrape', methods=['GET'])
def scrape_menu():
    menu = scraper.scrape_menu()
    return jsonify(menu)

# API endpoint to get a list of meal plans for the given nutritional goals.
@app.route('/api/mealplan', methods=['POST'])
def get_meal_plan():
    user_goals = request.get_json()
    # Ensure numeric conversion for the goals if coming from JSON (they may be strings)
    numeric_goals = {
        "calories": float(user_goals.get("calories", 0)),
        "fats": float(user_goals.get("fats", 0)),
        "carbs": float(user_goals.get("carbs", 0)),
        "proteins": float(user_goals.get("proteins", 0))
    }
    plans = calculate_meal_plans(numeric_goals, max_meals=4, top_n=10)
    # Return the candidate plans as JSON.
    return jsonify(plans)

if __name__ == "__main__":
    app.run(debug=True)
