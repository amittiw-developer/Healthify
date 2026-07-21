import re


# ---------------- DO NOT TOUCH WORDS ----------------
# medical meaning destroy nahi hona chahiye

PROTECTED_WORDS = [
    "urgent", "emergency", "critical", "severe",
    "high", "moderate", "mild",
    "cardiac", "chest pain", "breathing",
    "bleeding", "unconscious", "stroke",
    "heart", "attack", "pressure"
]


# ---------------- TEXT CLEAN ----------------

def clean_sentence(text: str):
    if not text:
        return ""

    original = str(text).strip()

    # agar medical severity words present hai → skip cleaning
    low_original = original.lower()
    if any(w in low_original for w in PROTECTED_WORDS):
        return original  # DO NOT MODIFY

    # safe soft cleaning only
    vague_words = [
        "may be", "could be", "possibly", "generally",
        "in some cases", "often", "usually happens when",
        "it appears that", "it seems", "kind of", "sort of"
    ]

    low = low_original
    for w in vague_words:
        low = low.replace(w, "")

    # remove extra spaces
    low = re.sub(r'\s+', ' ', low).strip()

    # capitalise
    return low.capitalize()


# ---------------- LIST CLEANER ----------------

def clean_list(items):

    if not isinstance(items, list):
        return []

    cleaned = []
    seen = set()

    for item in items:

        if not item:
            continue

        txt = str(item).strip()

        # keep medical items unchanged
        if any(w in txt.lower() for w in PROTECTED_WORDS):
            final = txt
        else:
            final = clean_sentence(txt)

        if len(final) < 3:
            continue

        if final not in seen:
            cleaned.append(final)
            seen.add(final)

    return cleaned[:6]  # allow slightly more medical items


# ---------------- MAIN FILTER ----------------

def filter_ai_response(ai_data: dict):

    if not isinstance(ai_data, dict):
        return ai_data

    return {
        # NEVER modify severity meaning
        "severity": str(ai_data.get("severity", "")).strip(),

        "observed_pattern": clean_sentence(ai_data.get("observed_pattern", "")),
        "care_recommendation": clean_sentence(ai_data.get("care_recommendation", "")),

        "precautions": clean_list(ai_data.get("precautions")),
        "consult_specialist": clean_list(ai_data.get("consult_specialist")),
        "suggested_tests": clean_list(ai_data.get("suggested_tests")),
        "home_relief": clean_list(ai_data.get("home_relief")),
    }