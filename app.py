# app.py
from flask import Flask, render_template, request, jsonify
from meal_planner import calculate_meal_plan
import scraper

app = Flask(__name__)

# Home route serves the HTML page.
@app.route('/')
def index():
    return render_template('index.html')

# Optional endpoint to manually trigger the menu scrape.
@app.route('/scrape', methods=['GET'])
def scrape_menu():
    menu = scraper.scrape_menu()
    return jsonify(menu)

# API endpoint to get a meal plan for the given nutritional goals.
@app.route('/api/mealplan', methods=['POST'])
def get_meal_plan():
    user_goals = request.get_json()
    meals, total_macros = calculate_meal_plan(user_goals)
    response = {
        "meals": meals,
        "total": total_macros
    }
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)
