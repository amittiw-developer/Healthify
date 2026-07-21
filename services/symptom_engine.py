from services.symptom_database import SYMPTOMS
from services.ai_bridge import ai_chat_response

import re
from difflib import SequenceMatcher


# =========================================================
# TEXT NORMALIZER
# =========================================================
def normalize(text: str):

    text = text.lower()

    replacements = {
        "aa": "a",
        "ee": "i",
        "oo": "u",
        "kh": "k",
        "ph": "f",
        "bh": "b",
        "sh": "s",
        "dh": "d",
        "th": "t"
    }

    for k, v in replacements.items():
        text = text.replace(k, v)

    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


# =========================================================
# SIMILARITY
# =========================================================
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def fuzzy_match(words, keyword_words):

    if all(any(similar(k, w) > 0.78 for w in words) for k in keyword_words):
        return True

    for i in range(len(words)):
        chunk = " ".join(words[i:i + len(keyword_words)])

        if similar(chunk, " ".join(keyword_words)) > 0.82:
            return True

    return False


# =========================================================
# CONTEXT VALIDATION
# =========================================================
def context_valid(symptom_name, words):

    words = set(words)

    if symptom_name == "eye_strain":
        return bool(words & {"ankh", "aankh", "eye", "eyes", "vision", "screen"})

    if symptom_name == "acidity":
        return bool(words & {"pet", "stomach", "seena", "chest", "khana", "meal", "gas"})

    if symptom_name == "dizziness":
        return bool(words & {"chakkar", "ghoom", "spin", "head", "utha", "khade"})

    return True


# =========================================================
# DETECT SYMPTOMS
# =========================================================
def detect_symptoms(user_text):

    text = normalize(user_text)
    words = text.split()

    detected = []

    for name, data in SYMPTOMS.items():

        for kw in data["keywords"]:

            kw_norm = normalize(kw)
            kw_words = kw_norm.split()

            if not fuzzy_match(words, kw_words):
                continue

            if not context_valid(name, words):
                continue

            detected.append(name)
            break

    return list(dict.fromkeys(detected))


# =========================================================
# HUMAN JOIN
# =========================================================
def join_human(items):

    if len(items) == 1:
        return items[0]

    if len(items) == 2:
        return items[0] + " and " + items[1]

    return ", ".join(items[:-1]) + " and " + items[-1]


# =========================================================
# 🔥 AI FALLBACK RECOVERY
# =========================================================
def ai_recovery_fallback(user_text):

    prompt = f"""
User health issue: {user_text}

Give:

1. short possible explanation
2. short body insight
3. 4 recovery actions separated by •

Format exactly:

CAUSE:
...

EFFECT:
...

SOLUTION:
action • action • action • action
"""

    response = ai_chat_response(prompt)

    if not response:
        return {
            "cause": "Your body may need some recovery support today.",
            "effect": "Some temporary imbalance may be affecting your comfort.",
            "solution": "Hydrate • Proper rest • Light meals • Observe symptoms"
        }

    try:

        cause = ""
        effect = ""
        solution = ""

        lines = response.splitlines()

        current = ""

        for line in lines:

            line = line.strip()

            if line.startswith("CAUSE:"):
                current = "cause"
                cause = line.replace("CAUSE:", "").strip()

            elif line.startswith("EFFECT:"):
                current = "effect"
                effect = line.replace("EFFECT:", "").strip()

            elif line.startswith("SOLUTION:"):
                current = "solution"
                solution = line.replace("SOLUTION:", "").strip()

            else:

                if current == "cause":
                    cause += " " + line

                elif current == "effect":
                    effect += " " + line

                elif current == "solution":
                    solution += " " + line

        if not solution:
            solution = "Hydrate • Proper rest • Observe symptoms • Healthy routine"

        return {
            "cause": cause.strip(),
            "effect": effect.strip(),
            "solution": solution.strip()
        }

    except Exception:

        return {
            "cause": "Your body may need recovery support today.",
            "effect": "Some temporary imbalance may be affecting your comfort.",
            "solution": "Hydrate • Proper rest • Light meals • Observe symptoms"
        }


# =========================================================
# FINAL RESPONSE ENGINE
# =========================================================
def build_response(user_text):

    detected = detect_symptoms(user_text)

    # =====================================================
    # 🔥 AI SMART FALLBACK
    # =====================================================
    if not detected:

        return ai_recovery_fallback(user_text)

    causes = []
    effects = []
    solutions = []

    for symptom in detected:

        data = SYMPTOMS.get(symptom)

        if not data:
            continue

        causes.append(data["why"])

        effects.append(
            symptom.replace("_", " ")
        )

        solutions.extend(data["care"])

    # remove duplicates
    def unique(seq):

        seen = set()
        out = []

        for x in seq:

            if x not in seen:
                seen.add(x)
                out.append(x)

        return out

    causes = unique(causes)
    effects = unique(effects)
    solutions = unique(solutions)

    cause_text = join_human(causes[:2])

    effect_text = (
        "Your body is showing signs related to "
        + join_human(effects[:3])
        + "."
    )

    solution_text = " • ".join(solutions[:8])

    return {
        "cause": cause_text,
        "effect": effect_text,
        "solution": solution_text
    }