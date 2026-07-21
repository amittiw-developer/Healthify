# services/triage_engine.py

import re

# -------------------------------------------------------
# TEXT NORMALIZATION (HINGLISH + TYPOS + USER STYLE)
# -------------------------------------------------------

def normalize(text: str):
    if not text:
        return ""

    text = text.lower()

    # common hindi / hinglish medical words
    replacements = {
        "baaye": "left",
        "baye": "left",
        "left side": "left",
        "seena": "chest",
        "chhati": "chest",
        "dil": "heart",
        "saans": "breath",
        "sans": "breath",
        "saans phoolna": "breathless",
        "ghabrahat": "anxiety",
        "dard": "pain",
        "jalan": "burning",
        "dabav": "pressure",
        "bojh": "pressure",
        "sunn": "numb",
        "sunpan": "numbness",
        "chakkar": "dizziness",
        "behosh": "faint",
    }

    for k, v in replacements.items():
        text = text.replace(k, v)

    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


# -------------------------------------------------------
# HISTORY KEYWORDS
# -------------------------------------------------------

CARDIAC_HISTORY = [
    "heart surgery", "valve replacement", "bypass",
    "angioplasty", "stent", "pacemaker", "cardiac surgery",
    "open heart", "heart operation", "heart patient"
]


# -------------------------------------------------------
# SYMPTOM GROUPS
# -------------------------------------------------------

CHEST_SIGNS = [
    "chest pain", "left chest", "heart pain",
    "pressure chest", "tightness chest",
    "burning chest", "chest pressure"
]

BREATH_SIGNS = [
    "shortness breath", "breath difficulty", "breathless",
    "cannot breathe", "breathing problem"
]

RADIATING_SIGNS = [
    "pain arm", "pain left arm", "pain jaw",
    "pain shoulder", "radiating pain"
]

COLLAPSE_SIGNS = [
    "faint", "blackout", "collapse", "unconscious"
]

NEURO_SIGNS = [
    "numbness", "slurred speech", "weakness one side",
    "face drooping"
]


# -------------------------------------------------------
# SMART MATCH
# -------------------------------------------------------

def contains_any(text, keywords):
    return any(k in text for k in keywords)


# -------------------------------------------------------
# TRIAGE DECISION ENGINE
# -------------------------------------------------------

def triage_level(user_text: str, history: str):

    text = normalize(user_text + " " + history)

    has_history = contains_any(text, CARDIAC_HISTORY)
    chest = contains_any(text, CHEST_SIGNS)
    breath = contains_any(text, BREATH_SIGNS)
    radiation = contains_any(text, RADIATING_SIGNS)
    collapse = contains_any(text, COLLAPSE_SIGNS)
    neuro = contains_any(text, NEURO_SIGNS)

    # 🚨 LEVEL 1 — LIFE THREATENING
    if collapse or neuro:
        return "emergency"

    if has_history and (chest or breath or radiation):
        return "emergency"

    # 🚨 LEVEL 2 — VERY HIGH RISK
    if chest and breath:
        return "urgent"

    if chest and radiation:
        return "urgent"

    # ⚠️ LEVEL 3 — NEEDS DOCTOR
    if chest:
        return "attention"

    if "pain" in text and has_history:
        return "attention"

    # 🟢 LEVEL 4 — NORMAL
    return "normal"


# -------------------------------------------------------
# AI OVERRIDE (CRITICAL SAFETY LAYER)
# -------------------------------------------------------

def apply_triage_override(ai_data: dict, level: str):

    if not ai_data:
        ai_data = {}

    if level == "emergency":
        ai_data["severity"] = "Critical"
        ai_data["observed_pattern"] = "Symptoms may indicate a serious cardiac condition"
        ai_data["care_recommendation"] = "Go to the nearest emergency department immediately"
        ai_data["consult_specialist"] = ["Cardiologist"]
        ai_data["precautions"] = [
            "Do not ignore symptoms",
            "Avoid physical exertion",
            "Do not drive yourself"
        ]
        ai_data["home_relief"] = []

    elif level == "urgent":
        ai_data["severity"] = "High"
        ai_data["care_recommendation"] = "Medical evaluation required today"
        ai_data["consult_specialist"] = ["Physician or Cardiologist"]

    elif level == "attention":
        ai_data["severity"] = "Moderate"

    else:
        ai_data.setdefault("severity", "Mild")

    return ai_data