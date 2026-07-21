# ==========================================================
# HEALTHIFY SYMPTOM KNOWLEDGE BASE
# deterministic medical awareness engine
# ==========================================================

SYMPTOMS = {

# ----------------------------------------------------------
# HEAD & NEURO
# ----------------------------------------------------------

"headache": {
    "keywords": ["sar dard","sirdard","sir dard","headache","head pain","head heavy","dimag bhari"],
    "why": "Often linked to dehydration, mental stress, eye strain, or lack of sleep.",
    "care": ["Drink water","Rest in a calm environment","Limit screen exposure"]
},

"dizziness": {
    "keywords": ["chakkar","dizziness","ghoom raha","utha to chakkar"],
    "why": "Commonly occurs due to low hydration, sudden posture change, or low blood pressure.",
    "care": ["Sit down immediately","Drink fluids","Stand slowly"]
},

"fatigue": {
    "keywords": ["thakan","weakness","kamjori","tired","low stamina"],
    "why": "Usually related to poor sleep, nutritional deficiency, or physical overexertion.",
    "care": ["Proper sleep","Balanced meals","Stay hydrated"]
},

"anxiety": {
    "keywords": ["ghabrahat","bechaini","restlessness","uneasy","panic"],
    "why": "Often triggered by stress hormones affecting breathing and heart rhythm.",
    "care": ["Slow breathing","Short walk","Reduce caffeine"]
},

# ----------------------------------------------------------
# EYES
# ----------------------------------------------------------

"eye_strain": {
    "keywords": ["aankh jalan","ankho me jalan","eye burning","eye strain","aankh bhari","screen headache","mobile se aankh"],
    "why": "Usually caused by prolonged screen exposure reducing blinking and drying the eye surface.",
    "care": ["Follow 20-20-20 rule","Blink frequently","Reduce brightness"]
},

"eye_irritation": {
    "keywords": ["aankh lal","red eye","watering eyes","aankh pani"],
    "why": "Often due to allergy, dust exposure, or irritation of the eye surface.",
    "care": ["Wash with clean water","Avoid rubbing","Limit screen use"]
},

# ----------------------------------------------------------
# RESPIRATORY
# ----------------------------------------------------------

"cough": {
    "keywords": ["khansi","cough","sukhi khansi","balgam wali khansi"],
    "why": "Commonly caused by throat irritation, infection, or environmental triggers.",
    "care": ["Warm fluids","Steam inhalation","Avoid cold air"]
},

"sore_throat": {
    "keywords": ["gala dard","gala kharab","throat pain","hoarseness"],
    "why": "Usually due to viral irritation or excessive voice use.",
    "care": ["Warm salt gargle","Avoid cold drinks","Voice rest"]
},

"nasal_congestion": {
    "keywords": ["naak band","nose blocked","naak behna","sneezing"],
    "why": "Often occurs due to cold, allergy, or sinus inflammation.",
    "care": ["Steam inhalation","Stay warm","Hydration"]
},

"breathlessness": {
    "keywords": ["saans phoolna","breathlessness","saans lene me dikkat"],
    "why": "Can occur due to exertion, anxiety, or airway irritation.",
    "care": ["Rest","Slow breathing","Fresh air"]
},

# ----------------------------------------------------------
# DIGESTION
# ----------------------------------------------------------

"acidity": {
    "keywords": ["acidity","pet jalan","heartburn","seene me jalan","gas"],
    "why": "Usually triggered by spicy food, irregular meals, or late eating.",
    "care": ["Eat light food","Avoid spicy meals","Do not lie down after eating"]
},

"indigestion": {
    "keywords": ["pet kharab","indigestion","dyspepsia","khana hazam nahi"],
    "why": "Digestive discomfort occurs when the stomach struggles to process heavy food.",
    "care": ["Light meals","Eat slowly","Avoid overeating"]
},

"nausea": {
    "keywords": ["ultee jesa","nausea","vomit feel","mann ghabra raha"],
    "why": "Often related to acidity, empty stomach, or temporary gastric irritation.",
    "care": ["Sip fluids slowly","Avoid oily food","Rest"]
},

"diarrhea": {
    "keywords": ["loose motion","dast","diarrhea"],
    "why": "Usually due to food contamination or stomach infection.",
    "care": ["ORS fluids","Light diet","Avoid dairy temporarily"]
},

"constipation": {
    "keywords": ["kabz","constipation","hard stool"],
    "why": "Often caused by low fiber intake and dehydration.",
    "care": ["Increase water","Eat fruits","Regular walking"]
},

# ----------------------------------------------------------
# MUSCLE & JOINT
# ----------------------------------------------------------

"body_pain": {
    "keywords": ["body pain","body toot","jism dard","limb pain"],
    "why": "Usually muscle fatigue from overuse, poor sleep, or mild viral response.",
    "care": ["Warm shower","Gentle stretching","Rest"]
},

"back_pain": {
    "keywords": ["kamar dard","back pain","lower back pain"],
    "why": "Commonly due to posture strain or long sitting.",
    "care": ["Correct posture","Stretch","Warm compress"]
},

"neck_pain": {
    "keywords": ["gardan dard","neck pain"],
    "why": "Often caused by prolonged mobile use or bad sleeping position.",
    "care": ["Neck stretches","Correct pillow height","Limit screen tilt"]
},

"knee_pain": {
    "keywords": ["ghutna dard","knee pain"],
    "why": "Usually due to joint stress or prolonged standing.",
    "care": ["Avoid strain","Light movement","Warm compress"]
},

# ----------------------------------------------------------
# GENERAL
# ----------------------------------------------------------

"fever": {
    "keywords": ["bukhar","fever","temperature","viral lag raha"],
    "why": "Indicates immune system activity against infection.",
    "care": ["Rest","Hydration","Monitor temperature"]
},

"sleep_issue": {
    "keywords": ["neend nahi","insomnia","sleep problem"],
    "why": "Often linked to stress hormones and irregular sleep timing.",
    "care": ["Fixed sleep schedule","Avoid screens before bed","Relaxation breathing"]
},

"general_malaise": {
    "keywords": ["thik nahi lag raha","body heavy","uneasy"],
    "why": "May occur when the body is tired or mildly unwell without a specific cause.",
    "care": ["Rest","Hydration","Light meals"]
}

}
