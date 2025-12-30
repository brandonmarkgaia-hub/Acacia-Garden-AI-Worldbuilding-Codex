import time
from google.generativeai import GenerativeModel

MODEL = "models/gemini-2.0-flash"

def call(prompt):
    model = GenerativeModel(MODEL)
    for attempt in range(5):
        try:
            return model.generate_content(prompt).text
        except Exception as e:
            if "429" in str(e):
                time.sleep(2 ** attempt)
            else:
                raise
