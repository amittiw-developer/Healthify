from services.vector_store import vector_store
from services.dataset_loader import dataset
from services.symptom_interpreter import analyze_symptoms, split_user_symptoms
from langdetect import detect
import re


# =====================================================
# LANGUAGE DETECTION
# =====================================================
def detect_language_safe(text: str):
    if not text:
        return "english"
    try:
        lang = detect(text)
        if lang in ["hi", "mr", "ne"]:
            return "hinglish"
        return "english"
    except:
        return "english"


# =====================================================
# SMART SYMPTOM PARSER
# =====================================================
SYMPTOM_PATTERNS = {
    "headache": ["sar dard","sardard","headache","migraine","head pain"],
    "body_pain": ["body pain","bodypain","jism dard","body toot","thakan dard"],
    "back_pain": ["kamar dard","back pain","lower back"],
    "eye_burning": ["aankh jalan","ankho me jalan","eye burning","burning eyes"],
    "nausea": ["ultee","nausea","vomiting feel","ghabrahat pet"],
    "fever": ["bukhar","fever","temperature"],
    "fatigue": ["weakness","thakan","tired","energy low"]
}

def extract_symptoms(text):
    text = text.lower()
    found = []
    for label,patterns in SYMPTOM_PATTERNS.items():
        for p in patterns:
            if re.search(rf"\b{re.escape(p)}\b", text):
                found.append(label)
                break
    return list(set(found))


# =====================================================
# CLINICAL PRIORITY ENGINE (Doctor Logic)
# =====================================================
def detect_conditions(symptoms):

    symptoms = set(symptoms)
    result = []

    # Specific organ problems FIRST
    if "eye_burning" in symptoms:
        result.append("eye_strain")

    # Neurological
    if "headache" in symptoms and "eye_burning" in symptoms:
        result.append("migraine")

    # Digestive
    if "nausea" in symptoms:
        result.append("gastric")

    # Musculoskeletal
    if "back_pain" in symptoms or "body_pain" in symptoms:
        result.append("muscle_strain")

    # Viral LAST
    if "fever" in symptoms or "fatigue" in symptoms:
        result.append("viral")

    # remove duplicates preserve order
    final=[]
    for r in result:
        if r not in final:
            final.append(r)

    return final[:2]


# =====================================================
# SAFE HELPERS
# =====================================================
def to_list(value):
    if not value:
        return []
    if isinstance(value,list):
        return [str(v).strip() for v in value if v]
    if isinstance(value,str):
        return [value.strip()]
    return [str(value)]


def normalize_indices(indices):
    try:
        if hasattr(indices,"tolist"):
            indices=indices.tolist()
    except:
        pass
    flat=[]
    if isinstance(indices,list):
        for i in indices:
            if isinstance(i,list):
                flat.extend(i)
            else:
                flat.append(i)
    return [int(x) for x in flat if isinstance(x,(int,float))]


# =====================================================
# MAIN RESPONSE ENGINE
# =====================================================
def generate_health_response(user_text):

    language = detect_language_safe(user_text)

    explanations=[]
    actions=[]
    reassurance=""

    # =================================================
    # STEP 1 — CLINICAL UNDERSTANDING
    # =================================================
    parsed_symptoms = extract_symptoms(user_text)
    priority_conditions = detect_conditions(parsed_symptoms)

    if priority_conditions:

        if "eye_strain" in priority_conditions:
            explanations.append(
                "Eye burning commonly occurs due to dryness or prolonged screen focus causing strain."
            )
            actions += ["Follow 20-20-20 rule","Blink frequently","Reduce screen brightness"]

        if "migraine" in priority_conditions:
            explanations.append(
                "Headache with eye discomfort suggests sensory overload or migraine trigger."
            )
            actions += ["Rest in dim light","Stay hydrated"]

        if "gastric" in priority_conditions:
            explanations.append(
                "Nausea usually comes from temporary digestive imbalance or acidity."
            )
            actions += ["Light meals","Avoid oily food"]

        if "muscle_strain" in priority_conditions:
            explanations.append(
                "Body or back pain typically indicates muscle fatigue or posture strain."
            )
            actions += ["Gentle stretching","Warm compress"]

        if "viral" in priority_conditions:
            explanations.append(
                "Combination of fatigue and fever may indicate early viral response."
            )
            actions += ["Rest","Warm fluids","Monitor temperature"]

        reassurance="Currently mild pattern — observe for 24 hours"

        return {
            "explanations": explanations[:2],
            "actions": actions[:4],
            "reassurance": reassurance
        }

    # =================================================
    # STEP 2 — RULE ENGINE FALLBACK
    # =================================================
    quick_results = analyze_symptoms(user_text)
    for r in quick_results:
        explanations += to_list(r.get("body"))
        actions += to_list(r.get("action"))

    # =================================================
    # STEP 3 — VECTOR KNOWLEDGE FALLBACK
    # =================================================
    used_body_parts=set()
    symptoms = split_user_symptoms(user_text)

    for symptom in symptoms:

        raw_indices=vector_store.search(symptom,top_k=2)
        indices=normalize_indices(raw_indices)

        for idx in indices:

            entry=dataset.get_entry(idx)
            if not entry:
                continue

            body_part=entry.get("body_part","general")
            if body_part in used_body_parts:
                continue
            used_body_parts.add(body_part)

            explanations+=to_list(entry.get("friendly_explanation_english"))
            actions+=to_list(entry.get("action_steps_english"))
            reassurance=entry.get("reassurance_english") or reassurance

    # =================================================
    # CLEANUP
    # =================================================
    explanations=[e for e in dict.fromkeys(explanations) if e.strip()]
    actions=[a for a in dict.fromkeys(actions) if a.strip()]

    explanations=explanations[:2]
    actions=actions[:4]

    if not explanations:
        explanations=["Your body seems slightly out of routine today."]
        actions=["Hydrate well","Sleep on time","Light movement"]
        reassurance="Nothing serious detected."

    if not reassurance:
        reassurance="Monitor symptoms and maintain routine."

    return {
        "explanations": explanations,
        "actions": actions,
        "reassurance": reassurance
    }
