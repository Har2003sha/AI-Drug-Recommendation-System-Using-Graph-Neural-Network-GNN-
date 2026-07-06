import os
import joblib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "models", "drug_model.pkl")
VECTORIZER_PATH = os.path.join(BASE_DIR, "models", "vectorizer.pkl")

class DrugModel:

    def __init__(self):

        self.model = joblib.load(MODEL_PATH)
        self.vectorizer = joblib.load(VECTORIZER_PATH)

    def predict(self, drug_name, condition):

        text = str(drug_name) + " " + str(condition)

        text_vec = self.vectorizer.transform([text])

        prediction = self.model.predict(text_vec)[0]

        # confidence (approx)
        try:
            probs = self.model.predict_proba(text_vec)
            confidence = round(max(probs[0]) * 100, 2)
        except:
            confidence = 0

        return prediction, confidence