import re

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

    text=text.lower()
    found=[]

    for label,patterns in SYMPTOM_PATTERNS.items():
        for p in patterns:
            if re.search(rf"\b{re.escape(p)}\b",text):
                found.append(label)
                break

    return list(set(found))
