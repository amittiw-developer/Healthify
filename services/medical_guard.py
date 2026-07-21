# services/medical_guard.py

import re

# ---------------- NORMALISE TEXT ----------------

def normalize(text: str):
    if not text:
        return ""

    text = text.lower()

    # hinglish variations
    replacements = {
        "baaye": "left",
        "baye": "left",
        "left side": "left",
        "seene": "chest",
        "seena": "chest",
        "chati": "chest",
        "chaati": "chest",
        "dil": "heart",
        "dhadkan": "heartbeat",
        "saans": "breath",
        "sans": "breath",
        "phool rahi": "breathlessness",
        "dard": "pain",
        "jalan": "burning",
        "dabav": "pressure",
        "ghabrahat": "anxiety",
    }

    for k, v in replacements.items():
        text = text.replace(k, v)

    return text


# ---------------- HISTORY KEYWORDS ----------------

CARDIAC_HISTORY = [
    "heart surgery",
    "valve replacement",
    "bypass",
    "angioplasty",
    "stent",
    "cardiac surgery",
    "open heart",
    "cabg"
]

HIGH_RISK_DISEASE = [
    "heart",
    "cardiac",
    "bp",
    "blood pressure",
    "hypertension",
    "diabetes"
]

# ---------------- SYMPTOM RED FLAGS ----------------

CHEST_SYMPTOMS = [
    "chest pain",
    "left pain",
    "chest pressure",
    "tightness",
    "heart pain",
    "breathlessness",
    "breathing difficulty",
    "pressure in chest"
]

NEURO_SYMPTOMS = [
    "numbness",
    "weakness",
    "speech problem",
    "one side weak",
    "dizziness"
]


# ---------------- TEXT SEARCH ----------------

def contains_any(text, keywords):
    text = normalize(text)
    for word in keywords:
        if word in text:
            return True
    return False


# ---------------- RISK ENGINE ----------------

def evaluate_medical_risk(history: str, symptoms: str):

    history_n = normalize(history)
    symptoms_n = normalize(symptoms)

    # CARDIAC EMERGENCY
    if contains_any(history_n, CARDIAC_HISTORY) and contains_any(symptoms_n, CHEST_SYMPTOMS):
        return "URGENT"

    # HIGH RISK PATIENT + CHEST
    if contains_any(history_n, HIGH_RISK_DISEASE) and contains_any(symptoms_n, CHEST_SYMPTOMS):
        return "PRIORITY"

    # NEURO WARNING
    if contains_any(symptoms_n, NEURO_SYMPTOMS):
        return "PRIORITY"

    return "NORMAL"


# ---------------- OVERRIDE REPORT ----------------

def apply_risk_override(report: dict, risk_level: str):

    if risk_level == "URGENT":
        report["severity"] = "High — Immediate medical attention recommended"
        report["what_to_do"] = "Do not wait at home. Go to nearest hospital immediately."
        report["monitor_for"] = "Avoid delay. Emergency evaluation required."
        report["reassurance"] = "Because of your medical history, this symptom must be medically checked now."

    elif risk_level == "PRIORITY":
        report["severity"] = "Moderate to High — Medical review advised"
        report["what_to_do"] = "Arrange a doctor consultation soon."
        report["monitor_for"] = "If symptoms worsen, visit emergency department."
        report["reassurance"] = "Medical evaluation is safer than home treatment in this case."

    return report