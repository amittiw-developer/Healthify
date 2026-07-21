# -------- HEALTHIFY SMART SYMPTOM INTERPRETER --------

def analyze_symptoms(text, lifestyle=None):

    # normalize
    if not text:
        text = ""

    s = text.lower().strip()

    # remove double spaces
    s = " ".join(s.split())

    results = []

    def has(words):
        return any(w in s for w in words)

    # --------------------------------------------------
    # FEVER / VIRAL
    # --------------------------------------------------
    if has([
        "fever","bukhar","bukhaar","bukar","tap","temperature",
        "body garam","jism garam","viral","kapkapi","thand lag"
    ]):
        results.append({
            "title":"Body Fighting Infection",
            "body":"Body immune response chala rahi hai — isliye weakness normal hai",
            "action":"Aaj rest + pani + light khichdi/daliya. Exercise skip."
        })

    # --------------------------------------------------
    # HEADACHE / SCREEN
    # --------------------------------------------------
    if has([
        "headache","sar dard","sir dard","sir bhaari","head pain",
        "screen pain","aankh dard","pressure head","migraine"
    ]):
        results.append({
            "title":"Brain Fatigue",
            "body":"Screen overload ya dehydration ka sign",
            "action":"20 min screen break + pani + aankhon ko rest"
        })

    # --------------------------------------------------
    # GAS / ACIDITY (CONTEXT AWARE FIX)
    # --------------------------------------------------
    acid_words = [
        "gas","acidity","pet jal","khatti dakaar",
        "burning chest","acid","pet me jalan","heavy lag"
    ]

    stomach_words = ["pet","chest","khana","stomach"]
    eye_words = ["aankh","ankh","eye","eyes"]

    if has(acid_words) or (
        "jalan" in s
        and has(stomach_words)
        and not has(eye_words)
    ):
        results.append({
            "title":"Acidity Trigger",
            "body":"Meal timing irregular hai",
            "action":"Empty stomach chai avoid + kela / saunf lo"
        })

    # --------------------------------------------------
    # FATIGUE / LOW ENERGY
    # --------------------------------------------------
    if has([
        "weakness","kamzori","thakan","low energy","tired",
        "fatigue","energy nahi","jaan nahi","haalka lag"
    ]):
        results.append({
            "title":"Low Energy Recovery",
            "body":"Sleep ya nutrition incomplete",
            "action":"Nimbu pani / coconut water + early sleep"
        })

    # --------------------------------------------------
    # DIZZINESS
    # --------------------------------------------------
    if has([
        "chakkar","dizzy","light headed","ghoom raha",
        "sar halka","khade hote chakkar"
    ]):
        results.append({
            "title":"Hydration Drop",
            "body":"BP ya pani kam hone ka signal",
            "action":"Baitho + dheere pani piyo + sudden movement avoid"
        })

    # --------------------------------------------------
    # COLD / COUGH
    # --------------------------------------------------
    if has([
        "cough","khansi","cold","jukam","sardi","naak beh",
        "gala dard","gala kharab","sneezing"
    ]):
        results.append({
            "title":"Respiratory Irritation",
            "body":"Season change reaction",
            "action":"Steam + warm water"
        })

    # --------------------------------------------------
    # BODY PAIN
    # --------------------------------------------------
    if has([
        "body pain","jism dard","back pain","kamar dard",
        "pair dard","muscle pain","body ache"
    ]):
        results.append({
            "title":"Muscle Recovery",
            "body":"Overuse ya viral fatigue",
            "action":"Garam shower + halka stretch"
        })

    # --------------------------------------------------
    # STRESS / ANXIETY
    # --------------------------------------------------
    if has([
        "stress","tension","ghabrahat","anxiety","restless",
        "mann ghabra","dil tez","bechaini"
    ]):
        results.append({
            "title":"Nervous System Stress",
            "body":"Mind calm mode me nahi gaya",
            "action":"4-6 breathing 5 min + slow walk"
        })

    # --------------------------------------------------
    # SLEEP ISSUE
    # --------------------------------------------------
    if has([
        "sleep nahi","neend nahi","so nahi paya","raat bhar jag",
        "late soya","baar baar uth"
    ]):
        results.append({
            "title":"Sleep Debt",
            "body":"Body repair incomplete",
            "action":"Aaj 30 min jaldi so"
        })

    # --------------------------------------------------
    # NO SYMPTOMS BUT IMPROVEMENT NEEDED
    # --------------------------------------------------
    if not results:
        results.append({
            "title":"Daily Body Optimization",
            "body":"Koi disease signal nahi — lifestyle fine tuning chahiye",
            "action":"Hydration + sunlight + 20 min walk = energy boost"
        })

    return results


# -------- AI SYMPTOM SPLITTER --------

SEPARATORS = [" aur ", " and ", ",", " with ", " plus ", "&"]

def split_user_symptoms(text: str):
    if not text:
        return []

    t = text.lower()

    for sep in SEPARATORS:
        t = t.replace(sep, "|")

    parts = [p.strip() for p in t.split("|") if len(p.strip()) > 2]

    cleaned = []
    for p in parts:
        if not any(p in c or c in p for c in cleaned):
            cleaned.append(p)

    if not cleaned:
        cleaned = [t]

    return cleaned
