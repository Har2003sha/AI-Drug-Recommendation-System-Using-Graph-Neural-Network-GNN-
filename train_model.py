import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier

########################################################
# Paths
########################################################

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_PATH = os.path.join(
    BASE_DIR,
    "dataset",
    "drugs_side_effects_drugs_com.csv"
)

MODEL_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_PATH = os.path.join(MODEL_DIR, "drug_model.pkl")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "vectorizer.pkl")

########################################################
# Load Dataset
########################################################

print("Loading dataset...")

df = pd.read_csv(DATA_PATH, low_memory=False)

df.columns = (
    df.columns.str.strip().str.lower().str.replace(" ", "_")
)

print("Columns:", df.columns.tolist())

########################################################
# Handle missing columns safely
########################################################

required_cols = ["drug_name", "medical_condition", "activity"]

for col in required_cols:
    if col not in df.columns:
        raise Exception(f"Missing column: {col}")

df = df.dropna(subset=required_cols)

########################################################
# Feature Engineering (TEXT INPUT)
########################################################

df["text"] = (
    df["drug_name"].astype(str) + " " +
    df["medical_condition"].astype(str)
)

########################################################
# Target variable
########################################################

y = df["activity"].astype(str)

########################################################
# Train/Test Split
########################################################

X_train, X_test, y_train, y_test = train_test_split(
    df["text"],
    y,
    test_size=0.2,
    random_state=42
)

########################################################
# TF-IDF Vectorizer
########################################################

vectorizer = TfidfVectorizer(
    max_features=5000,
    stop_words="english"
)

X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

########################################################
# Model (Random Forest)
########################################################

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)

model.fit(X_train_vec, y_train)

########################################################
# Save Model
########################################################

joblib.dump(model, MODEL_PATH)
joblib.dump(vectorizer, VECTORIZER_PATH)

print("Model Training Completed")
print("Model saved at:", MODEL_PATH)
print("Vectorizer saved at:", VECTORIZER_PATH)