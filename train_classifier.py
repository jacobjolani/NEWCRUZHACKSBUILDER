# train_classifier.py
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import pickle

# 1) Build or load your labeled dataset of strings
# For demonstration, let's embed a small sample dataset.
# In practice, place this in a CSV or JSON that you load.
data_samples = [
    ("Beef Barbacoa", "food"),
    ("Scrambled Eggs", "food"),
    ("Turkey Sausage Link", "food"),
    ("Latin-style Sauteed Chicken Vegan", "food"),
    ("Spinach & Monterey Jack Eggs Scramble", "food"),
    ("Meal Hours:", "not_food"),
    ("Contact us for catering", "not_food"),
    ("Allergen Information", "not_food"),
    ("Calorie Info", "not_food"),
    ("Dining Hall Hours", "not_food"),
    ("Upcoming Events", "not_food"),
]

# Convert to DataFrame
df = pd.DataFrame(data_samples, columns=["text", "label"])

# 2) Split data into features and labels
X = df["text"].values
y = df["label"].values

# 3) Vectorize text (TF-IDF)
vectorizer = TfidfVectorizer(
    lowercase=True,
    stop_words="english",
    ngram_range=(1, 2),        # can adjust to capture bigrams
    min_df=1
)
X_vec = vectorizer.fit_transform(X)

# 4) Train a classifier (Logistic Regression, Naive Bayes, etc.)
clf = LogisticRegression(random_state=42)
clf.fit(X_vec, y)

# 5) Save the model and the vectorizer to disk
with open("food_classifier.pkl", "wb") as f:
    pickle.dump((vectorizer, clf), f)

print("Model training complete. Saved to food_classifier.pkl")
