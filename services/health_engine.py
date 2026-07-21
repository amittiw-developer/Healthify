import random
import re


# ---------------- WORD MATCH ----------------
def has_word(text, words):
    for w in words:
        if re.search(rf"\b{re.escape(w)}\b", text):
            return True
    return False


# ---------------- SYMPTOM DETECTOR ----------------
def detect(symptoms):

    if not symptoms:
        return ["general"]

    s = symptoms.lower()

    detected = []

    if has_word(s, ["fever","bukhar","temperature","viral"]):
        detected.append("infection")

    if has_word(s, ["headache","sir dard","migraine"]):
        detected.append("headache")

    if has_word(s, ["cold","cough","khansi","sardi","throat"]):
        detected.append("respiratory")

    if has_word(s, ["stomach","pet dard","gas","acidity","indigestion","loose motion"]):
        detected.append("digestion")

    if has_word(s, ["weakness","thakan","fatigue","low energy"]):
        detected.append("fatigue")

    if has_word(s, ["chakkar","dizziness","ghoomna","bp","pressure"]):
        detected.append("bp")

    if not detected:
        detected.append("general")

    return list(dict.fromkeys(detected))


# ---------------- TEXT ENGINE ----------------
def generate_text(symptoms):

    detected = detect(symptoms)

    messages = {
        "infection":"Your body is responding to an infection. Hydration and rest support immune recovery.",
        "headache":"Headache often linked with stress, screen exposure or dehydration.",
        "respiratory":"Respiratory irritation detected. Warm fluids and steam inhalation may help.",
        "digestion":"Digestive imbalance observed. Avoid oily and spicy food.",
        "fatigue":"Body energy levels are low. Nutrition and sleep recovery needed.",
        "bp":"Possible blood pressure fluctuation. Stay hydrated and avoid sudden standing.",
        "general":"Maintain healthy routine and monitor symptoms."
    }

    return " ".join(messages[d] for d in detected if d in messages)


# ---------------- TEST SUGGESTION ----------------
def suggest_tests(symptoms):

    detected = detect(symptoms)

    test_map = {
        "infection":["CBC Test","CRP Test"],
        "respiratory":["Chest Checkup","Oxygen Saturation"],
        "headache":["Blood Pressure Test","Eye Checkup"],
        "digestion":["Liver Function Test","Ultrasound Abdomen"],
        "bp":["Blood Pressure Monitoring"],
        "fatigue":["Vitamin B12","Hemoglobin"],
        "general":["Basic Health Checkup","Blood Sugar Test"]
    }

    tests=[]
    for d in detected:
        tests += test_map.get(d,[])

    # preserve order + remove duplicates
    seen=set()
    ordered=[]
    for t in tests:
        if t not in seen:
            seen.add(t)
            ordered.append(t)

    return ordered


# ---------------- HEALTH THOUGHT ----------------
def health_thought(symptoms):

    detected = detect(symptoms)

    thoughts = {
        "infection":"Rest accelerates immune recovery more than medication alone.",
        "digestion":"Gut health improves when you eat slowly and calmly.",
        "fatigue":"Energy builds during sleep, not during work.",
        "bp":"Hydration stabilizes blood circulation.",
        "general":"Consistency in routine heals body naturally."
    }

    for d in detected:
        if d in thoughts:
            return thoughts[d]

    return thoughts["general"]


# ---------------- PRECAUTIONS ----------------
precautions_map = {
    "infection":["Drink warm fluids","Take proper rest","Avoid cold foods","Monitor temperature"],
    "respiratory":["Steam inhalation","Avoid dust exposure","Warm liquids","Keep throat warm"],
    "digestion":["Avoid spicy food","Eat light meals","Do not skip meals","Stay hydrated"],
    "headache":["Reduce screen time","Stay hydrated","Proper sleep","Relax breathing"],
    "fatigue":["Increase nutrition intake","Proper sleep","Light exercise","Avoid overwork"],
    "bp":["Avoid sudden standing","Stay hydrated","Reduce salt intake","Regular monitoring"],
    "general":["Balanced diet","Regular sleep","Daily walk","Stay hydrated"]
}


def random_precautions(symptoms="general"):

    detected = detect(symptoms)
    pool=[]

    for d in detected:
        pool += precautions_map.get(d,[])

    if not pool:
        pool = precautions_map["general"]

    return random.sample(pool, min(4,len(pool)))


# ---------------- CONSULTATIONS ----------------
doctor_map = {
    "infection":["General Physician"],
    "respiratory":["General Physician"],
    "digestion":["Gastroenterologist"],
    "headache":["Neurologist"],
    "bp":["Cardiologist"],
    "fatigue":["Nutritionist"],
    "general":["General Physician"]
}


def random_consultations(symptoms="general"):

    detected = detect(symptoms)
    doctors=[]

    for d in detected:
        doctors += doctor_map.get(d,[])

    return list(dict.fromkeys(doctors))
