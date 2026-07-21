import os
import re
import json
import random

USE_AI_ASSISTANT = True

# =========================================================
# GROQ CLIENT
# =========================================================
try:
    from groq import Groq
    _groq_key = os.getenv("GROQ_API_KEY")
    client = Groq(api_key=_groq_key) if _groq_key else None
    AI_AVAILABLE = client is not None
except Exception as e:
    print("Groq init failed:", e)
    client = None
    AI_AVAILABLE = False


# =========================================================
# LANGUAGE DETECTION
# =========================================================
def detect_language(text: str) -> str:
    if not text:
        return "english"
    t = text.lower().strip()

    if re.search(r'[\u0900-\u097F]', t):
        return "hindi"

    hinglish_markers = [
        "hai", "nahi", "nhi", "kyu", "kya", "kaise", "kaisa", "kese",
        "bukhar", "dard", "sar", "pet", "thakan", "kamjori", "chakkar",
        "khansi", "sardi", "bhai", "yaar", "yrr", "mujhe", "mera", "meri",
        "acha", "accha", "thik", "theek", "haan", "haa", "kaafi", "bahut",
        "zyada", "abhi", "raat", "subah", "din", "kal", "aaj", "lagta",
        "lagti", "wajah", "thak", "pareshan", "ghabra", "neend", "khana",
    "english": [
        "Hey! 👋 I'm Healthify AI — your health and wellness companion. What's on your mind?",
        "Hi there! 👋 Feel free to ask me anything about your health, symptoms, or wellness.",
        "Hello! 👋 I'm here to help with health and wellness. What can I help you with today?",
    ],
    "hinglish": [
        "Hey! 👋 Main Healthify AI hoon — aapka health aur wellness companion. Kya poochna hai?",
        "Hii! 👋 Apni health se related koi bhi baat poochh sakte ho — main yahan hoon.",
        "Namaste! 👋 Health aur wellness ke baare mein kuch bhi poochho, main help karunga.",
    ],
    "hindi": [
        "नमस्ते! 👋 मैं Healthify AI हूं — आपका health साथी। क्या जानना है?",
        "हेलो! 👋 आपकी health से जुड़ी कोई भी बात पूछ सकते हैं।",
    ],
}

def is_greeting(text: str) -> bool:
    t = text.lower().strip().rstrip("!?,.")
    return t in _GREETINGS

def get_greeting_reply(lang: str) -> str:
    return random.choice(_GREETING_REPLIES.get(lang, _GREETING_REPLIES["english"]))


# =========================================================
# BYE / CLOSING DETECTION
# =========================================================
_BYE_PATTERNS = [
    r"\b(bye|goodbye|alvida|tata)\b",
    r"\b(good\s*night|goodnight|shubh\s*ratri|gud\s*night)\b",
    r"\b(kal\s*milte|phir\s*milenge|baad\s*mein\s*aata|chal\s*bye)\b",
    r"\b(take\s*care|khuda\s*hafiz)\b",
]
_BYE_REPLIES = {
    "hinglish": [
        "Bilkul, apna khayal rakhna. Health ya wellness se related kuch bhi ho toh Healthify MindCare AI hamesha help ke liye available hai.",
        "Good night. Aaj rest ko priority do, aur agar koi health concern continue ho toh qualified doctor se advice lena safe rahega.",
        "Take care. Aap jab bhi wapas aayenge, main safe aur responsible wellness guidance ke liye available rahunga.",
    ],
    "hindi": [
        "ठीक है! अपना ध्यान रखिए 🙂 कोई भी health concern हो तो आइए।",
        "शुभ रात्रि! 🌙 अच्छी नींद लें।",
    ],
    "english": [
        "Take care. Healthify MindCare AI is here whenever you need safe wellness guidance.",
        "Good night. Rest well, and please consult a qualified professional if any symptom feels serious or persistent.",
        "Goodbye for now. Stay mindful of your health, and come back anytime you need guidance.",
    ],
}

def is_bye(text: str) -> bool:
    t = text.lower().strip()
    return any(re.search(p, t) for p in _BYE_PATTERNS)

def get_bye_reply(lang: str) -> str:
    return random.choice(_BYE_REPLIES.get(lang, _BYE_REPLIES["english"]))


# =========================================================
# SAFETY / ABUSE BOUNDARY
# =========================================================
_ABUSE_OR_EXPLICIT_PATTERNS = [
    r"\b(fuck|sex chat|sexting|nude|porn|blowjob|handjob|boobs|dick pic|pussy pic)\b",
    r"\b(chutiya|madarchod|bhenchod|behenchod|gandu|gaand|randi|bsdk|bhosdi)\b",
]
_SEXUAL_HEALTH_PATTERNS = [
    r"\b(sexual health|sex problem|erection|erectile|premature ejaculation|period|periods|mensuration|menstruation|pregnancy|pregnant|contraception|condom|sti|std|hiv|vaginal|penis pain|private part|libido|fertility)\b",
    r"\b(gupt rog|period late|pregnant ho|ling|yoni|shighrapatan|nightfall|swapnadosh)\b",
]

def is_abusive_or_explicit(text: str) -> bool:
    t = text.lower()
    return any(re.search(p, t) for p in _ABUSE_OR_EXPLICIT_PATTERNS)

def is_sexual_health_query(text: str) -> bool:
    t = text.lower()
    return any(re.search(p, t) for p in _SEXUAL_HEALTH_PATTERNS)

def boundary_reply(lang: str) -> str:
    if lang == "hinglish":
        return "Main aapki help respectful aur safe wellness topics par kar sakta hoon. Agar concern sexual health, stress, relationship, ya body health se juda hai, use clear aur respectful words me batayein."
    if lang == "hindi":
        return "Main sirf safe aur respectful wellness guidance de sakta hoon. Agar sawal sexual health, stress, relationship ya body health se related hai, kripya use saaf aur respectful tareeke se batayein."
    return "I can help with respectful, safe wellness guidance. If your concern is about sexual health, stress, relationships, or body health, please describe it clearly and respectfully."

def sexual_health_boundary_reply(lang: str) -> str:
    if lang == "hinglish":
        return "Sexual health ke concern par main respectful aur awareness-level guidance de sakta hoon. Please age, symptom, duration, pain/discharge/bleeding, aur pregnancy/STI risk jaise details safe words me batayein; urgent pain, heavy bleeding, ya unsafe exposure ho to qualified doctor se consult karein."
    if lang == "hindi":
        return "Sexual health se jude sawal par main sirf respectful awareness guidance de sakta hoon. Kripya age, symptom, duration, pain/discharge/bleeding aur pregnancy/STI risk jaise details saaf shabdon me batayein; severe pain ya heavy bleeding ho to doctor se milen."
    return "I can help with respectful sexual-health awareness guidance. Please share age, symptom, duration, pain/discharge/bleeding, and pregnancy/STI risk in clear words; seek qualified care for severe pain, heavy bleeding, or unsafe exposure."


# =========================================================
# HOW ARE YOU DETECTION
# =========================================================
_HOW_ARE_YOU_PATTERNS = [
    r"\bhow are you\b", r"\bhow r u\b", r"\bkaise ho\b", r"\bkaise hain\b",
    r"\bkaisa hai\b", r"\bkya haal\b", r"\btum btao\b", r"\baap btao\b",
    r"\bkese ho\b", r"\bkya kar rahe\b", r"\bkya kr rhe\b",
    r"\bwhat are you doing\b", r"\bkya chal raha\b", r"\bsab theek\b",
]
_HOW_ARE_YOU_REPLIES = {
    "english": [
        "I'm just a program — no feelings, but fully here for you! 🙂 Any health topic on your mind?",
        "All good on my end! More importantly — how are YOU doing? Any health concern?",
    ],
    "hinglish": [
        "Main ek AI hoon, feelings nahi hoti — but tumhari health ke liye poori tarah ready hoon! 🙂 Koi concern hai?",
        "Bas kaam karta rehta hoon! 🙂 Tumhara koi health sawaal hai?",
    ],
    "hindi": [
        "मैं एक AI हूं — feelings नहीं हैं, लेकिन आपके लिए पूरी तरह तैयार हूं! 🙂 कोई health concern है?",
    ],
}

def is_how_are_you(text: str) -> bool:
    t = text.lower().strip()
    return any(re.search(p, t) for p in _HOW_ARE_YOU_PATTERNS)

def get_how_are_you_reply(lang: str) -> str:
    return random.choice(_HOW_ARE_YOU_REPLIES.get(lang, _HOW_ARE_YOU_REPLIES["english"]))


# =========================================================
# ACK WORDS
# =========================================================
_ACK_WORDS = {
    "ok", "okk", "okay", "hmm", "hmmm", "hm", "ohh", "oh",
    "acha", "accha", "thik", "thik h", "theek hai", "theek h",
    "haan", "haa", "ji", "bilkul", "nhi", "nah", "nope",
    "yep", "yup", "yeah", "yes", "sure", "alright", "noted",
    "fine", "good", "great", "nice", "cool", "wow",
    "thanks", "thank you", "shukriya", "got it", "understood",
    "samajh gaya", "samjh gya", "nothing", "nothinh",
    "kuch nhi", "kuch nahi", "nothing much",
}
_ACK_REPLIES = {
    "hinglish": [
        "Theek hai 🙂 Koi health concern ho toh batao.",
        "Haan 🙂 Kuch poochna ho toh zaroor poocho.",
        "Achha 🙂 Main yahan hoon agar kuch chahiye.",
    ],
    "hindi": [
        "ठीक है 🙂 कोई health concern हो तो बताइए।",
        "अच्छा 🙂 कुछ और जानना हो तो पूछिए।",
    ],
    "english": [
        "Got it 🙂 Let me know if anything comes up.",
        "Alright 🙂 Feel free to ask anything health-related.",
        "Sure 🙂 I'm here if you need anything.",
    ],
}

def get_ack_reply(lang: str) -> str:
    return random.choice(_ACK_REPLIES.get(lang, _ACK_REPLIES["english"]))


# =========================================================
# ACK CLASSIFIER
# =========================================================
def is_acknowledgement_ai(text: str) -> bool:
    if not AI_AVAILABLE or len(text.strip().split()) > 2:
        return False
    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0.0,
            max_tokens=3,
            timeout=10,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Binary classifier. Is this message ONLY a casual reaction, "
                        "acknowledgement, or filler with zero health content? "
                        "Reply YES or NO only."
                    )
                },
                {"role": "user", "content": f'"{text}"'}
            ]
        )
        return "YES" in resp.choices[0].message.content.strip().upper()
    except Exception as e:
        print("ACK classifier error:", e)
        return False


# =========================================================
# CONVERSATION MODE
# =========================================================
def detect_mode(text: str) -> str:
    t = text.lower().strip()
    emotional = [
        "stress", "tension", "anxiety", "nervous", "anxious", "dar",
        "ghabrahat", "sad", "alone", "depressed", "depression", "rejection",
        "overthink", "burnout", "pressure", "frustrated", "hopeless",
        "exhausted", "helpless", "akela", "pareshan", "demotivate", "dukhi",
        "ro raha", "ro rahi", "thak gaya", "thak gayi", "haar gaya",
        "haar gayi", "bahut bura", "numb", "empty", "worthless", "useless",
        "gussa", "angry", "hurt", "ignored", "sad", "lonely",
        "husband", "wife", "family", "ghar", "maayke", "sasural",
        "relationship", "pyaar", "love", "shaadi", "breakup",
    ]
    if any(re.search(rf"\b{re.escape(w)}\b", t) for w in emotional):
        return "emotional"

    long_term = [
        "months", "years", "saal", "long time", "baar baar", "regularly",
        "daily", "pehle se", "kafi time se", "kaafi dino se", "chronic",
        "hamesha", "aksar", "hafte se", "weeks", "mahine se", "since",
    ]
    if any(re.search(rf"\b{re.escape(w)}\b", t) for w in long_term):
        return "long_term"

    return "normal"


# =========================================================
# CHAT SYSTEM PROMPT
# =========================================================
def build_system_prompt(lang: str, mode: str) -> str:

    if lang == "hinglish":
        lang_block = (
            "LANGUAGE: Hinglish — warm, natural Hindi-English mix.\n"
            "Write the way a caring educated Indian friend talks — simple, direct, genuine.\n"
            'Good: "Door rehne par distance feel hona natural hai. Unhe call karo aur seedha bolo ki tumhe unki bahut yaad aa rahi hai."\n'
            'Bad: "Lagta hai aapko lagta hai ki... isliye aap... karein" — never this robotic structure.\n'
        )
    elif lang == "hindi":
        lang_block = (
            "LANGUAGE: Simple conversational Hindi — easy, warm, direct.\n"
            'Good: "दूर रहने पर अकेलापन feel होना बहुत normal है। उन्हें call करके सीधे बोलो।"\n'
        )
    else:
        lang_block = (
            "LANGUAGE: Simple warm English — like a caring friend, not a textbook.\n"
            'Good: "Being apart can make anyone feel disconnected. Just call him and tell him directly what you\'re feeling."\n'
        )

    if mode == "emotional":
        mode_block = (
            "USER STATE: Emotional — feeling hurt, frustrated, lonely, or stressed about relationships/family.\n"
            "APPROACH:\n"
            "1. First — acknowledge what they feel in ONE natural line. Make them feel heard.\n"
            "2. Then — give ONE clear, practical suggestion that actually helps.\n"
            "3. Keep it warm and real — like a friend who genuinely cares.\n"
            "NEVER start with 'Lagta hai' or 'It seems like' — be direct and human.\n"
            "NEVER repeat the same structure across multiple replies.\n"
            "VARY your openings: use the person's name sometimes, or start with the emotion directly.\n"
        )
    elif mode == "long_term":
        mode_block = (
            "USER STATE: Recurring or long-standing concern.\n"
            "Acknowledge the duration naturally. Give realistic guidance. Suggest check-up only if genuinely needed.\n"
        )
    else:
        mode_block = "USER STATE: Normal. Be calm, direct, specific to this situation.\n"

    return f"""You are Healthify AI — a professional health and wellness assistant. Calm, warm, human, trustworthy. NOT a doctor.

SCOPE: Physical health, mental wellness, sleep, nutrition, exercise, stress, emotional wellbeing, sexual health, reproductive health, lifestyle, relationships affecting health.

HUMAN INTELLIGENCE: Understand what users are REALLY saying. Respond the way a knowledgeable, caring friend would — not like a robot reading from a script.

RESPONSE RULES:
- Max 3 sentences — complete, never trailing off
- CRITICAL: You MUST respond in the EXACT same language the user just used. If the user's message is in pure English, you MUST respond in simple, pure English. DO NOT mix Hindi or Hinglish if the user spoke English! If they speak Hinglish, respond in Hinglish.
- Sound professional, supportive, respectful, and human. Never rude, sarcastic, childish, lazy, or scripted.
- Never diagnose, guarantee, prescribe medicine, or claim certainty
- Never invent or assume the user's name. Use a name only if the user clearly provides it in the current conversation.
- Ask for missing context only when it changes safety or practical guidance
- Ask one intelligent follow-up question when the concern is unclear and guessing could be unsafe
- For emotional, relationship, family, loneliness, or stress concerns, do not suggest blood tests or specialists unless clear medical red flags are described
- If red flags appear (chest pain, breathing difficulty, fainting, stroke-like symptoms, self-harm, severe bleeding), clearly advise urgent local medical help
- Start differently each time — never repeat the same opening structure
- NEVER use "Lagta hai aapko lagta hai" or any doubled phrase
- NEVER start every sentence with "Lagta hai" or "It seems"
- NEVER follow the pattern: "X lagta hai... isliye aap Y karein"
- Be direct and warm — state things clearly, don't hedge everything
- No filler: "I understand", "You are not alone", "As an AI"
- No motivational speeches, no excessive reassurance
- No fear-based language
- Never fabricate medical facts
- Keep the answer naturally short when the user asks something simple; do not force long responses

SPECIALISTS (only when relevant):
Fever → Physician | Skin → Dermatologist | Gut → Gastroenterologist
Heart → Cardiologist | Mental health → Psychologist | Women's → Gynecologist
Bones → Orthopedic | ENT → ENT Specialist | Thyroid → Endocrinologist

{lang_block}{mode_block}
VISION: Every response should feel human, warm, and leave the user clearer on what to do next."""


# =========================================================
# RESPONSE CLEANUP  — also catches "lagta hai" repetition
# =========================================================
def cleanup_response(text: str) -> str:
    if not text:
        return ""

    text = re.sub(r'\n{3,}', '\n\n', text)

    # Remove robotic filler sentences
    remove_patterns = [
        r"As an AI[,\s][^.!?]*[.!?]",
        r"I('m| am) just an AI[^.!?]*[.!?]",
        r"I('m| am) here for you[^.!?]*[.!?]",
        r"You('re| are) not alone in this[^.!?]*[.!?]",
        r"I('m| am) with you[^.!?]*[.!?]",
        r"That'?s (a )?(great|wonderful|good) (question|point|attitude)[^.!?]*[.!?]",
        r"feel free to (ask|reach out)[^.!?]*[.!?]",
        r"(main|I am) yahan hoon aapki madad ke liye[^.!?]*[.!?]",
        r"Bas aaram se baitho[^.!?]*[.!?]",
        r"hum aapke saath hain[^.!?]*[.!?]",
    ]
    for pattern in remove_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    # Fix "lagta hai aapko lagta hai" doubled phrase
    text = re.sub(
        r'lagta hai\s+aapko\s+lagta hai',
        'aapko',
        text,
        flags=re.IGNORECASE
    )
    # Fix "it seems like it seems"
    text = re.sub(
        r'it seems (like )?it seems',
        'it seems',
        text,
        flags=re.IGNORECASE
    )
    # Fix "lagta hai... isliye aap... karein" robotic pattern — soften it
    text = re.sub(
        r'lagta hai\s+aapko\s+lagta hai\s+ki\s+',
        'aap ',
        text,
        flags=re.IGNORECASE
    )

    # Fix dangling conjunctions
    for ending in ["jisse", "taaki", "aur", "kyunki", "lekin", "because",
                   "so", "therefore", "however", "but", "which", "and"]:
        if re.search(rf'\b{re.escape(ending)}\s*$', text, re.IGNORECASE):
            text = re.sub(rf'\s*\b{re.escape(ending)}\s*$', ".", text, flags=re.IGNORECASE)

    # Hard cap: 4 sentences max
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    if len(sentences) > 4:
        text = " ".join(sentences[:4])

    return re.sub(r' {2,}', ' ', text).strip()


def remove_unconfirmed_name_prefix(text: str, user_input: str) -> str:
    if not text:
        return ""
    user_text = (user_input or "").lower()
    match = re.match(r"^\s*([A-Z][a-zA-Z]{2,18}),\s+(.+)$", text, flags=re.DOTALL)
    if not match:
        return text
    possible_name = match.group(1)
    safe_openers = {
        "Healthify", "Hello", "Hey", "Hi", "Namaste", "Please", "Good",
        "Take", "Based", "What", "Your"
    }
    if possible_name in safe_openers or possible_name.lower() in user_text:
        return text
    cleaned = match.group(2).strip()
    if cleaned and cleaned[0].islower():
        cleaned = cleaned[0].upper() + cleaned[1:]
    return cleaned or text


# =========================================================
# MAIN CHAT FUNCTION
# =========================================================
def ai_chat_response(user_input: str, history: list = None) -> str:
    if not USE_AI_ASSISTANT or not AI_AVAILABLE:
        return "Healthify MindCare AI is temporarily unavailable. Please try again shortly. If your concern feels urgent, contact a qualified medical professional or local emergency support."

    user_input = user_input.strip()
    if len(user_input) < 2:
        return "Please share a little more detail so I can respond safely and usefully."

    lang = detect_language_from_history(user_input, history)

    if is_abusive_or_explicit(user_input):
        return boundary_reply(lang)
    if is_sexual_health_query(user_input) and len(user_input.split()) < 8:
        return sexual_health_boundary_reply(lang)

    # P1 — Emergency
    if is_emergency(user_input):
        if lang == "hinglish":
            return (
                "⚠️ Jo aap describe kar rahe hain woh serious lag raha hai. "
                "Please abhi 112 (emergency) ya 108 (ambulance) call karo "
                "ya kisi trusted insaan ko apne paas bulao. "
                "Main ek AI hoon — abhi real help chahiye tumhe."
            )
        if lang == "hindi":
            return (
                "⚠️ यह गंभीर लग रहा है। "
                "कृपया अभी 112 या 108 call करें "
                "या किसी भरोसेमंद को बुलाएं। "
                "मैं एक AI हूं — आपको अभी real help चाहिए।"
            )
        return (
            "⚠️ What you're describing sounds serious. "
            "Please call 112 or 108 right now "
            "or get someone you trust with you. "
            "I'm an AI — you need real help immediately."
        )

    # P2 — Greeting
    if is_greeting(user_input):
        return get_greeting_reply(lang)

    # P3 — Bye
    if is_bye(user_input):
        return get_bye_reply(lang)

    # P4 — How are you
    if is_how_are_you(user_input):
        return get_how_are_you_reply(lang)

    # P5 — Exact ACK
    if user_input.lower().strip() in _ACK_WORDS:
        return get_ack_reply(lang)

    # P6 — ACK classifier (≤2 words only)
    if len(user_input.strip().split()) <= 2 and is_acknowledgement_ai(user_input):
        return get_ack_reply(lang)

    # P7 — Full AI
    mode = detect_mode(user_input)
    system_prompt = build_system_prompt(lang, mode)

    messages = []
    if history:
        for item in history[-3:]:
            u = (item.get("user", "") or "")[:500]
            a = (item.get("ai", "") or "")[:500]
            if u and a:
                messages.append({"role": "user", "content": u})
                messages.append({"role": "assistant", "content": a})

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0.45,
            max_tokens=300,
            presence_penalty=0.4,
            frequency_penalty=0.4,
            timeout=20,
            messages=[
                {"role": "system", "content": system_prompt},
                *messages,
                {"role": "user", "content": user_input},
            ]
        )
        answer = response.choices[0].message.content.strip()
        answer = cleanup_response(answer)
        answer = remove_unconfirmed_name_prefix(answer, user_input)
        return answer if answer else "Please share a little more detail so I can guide you responsibly."

    except Exception as e:
        print("Chat AI error:", e)
        return "Healthify MindCare AI is having a technical issue right now. Please try again in a moment, and seek qualified medical help if the concern is serious or worsening."


# =========================================================
# REPORT AI
# =========================================================
REPORT_SYSTEM_PROMPT = """You are Healthify AI's intelligent report engine.

Your job: Read the user's complete profile. Understand what they are REALLY going through. Generate a warm, human, genuinely useful health report.

CORE INTELLIGENCE:

1. USE ALL PROFILE DATA — name, age, gender, location, past conditions, symptoms, duration, pain level, sleep, exercise, water intake. Make it personal.

2. UNDERSTAND THE REAL ISSUE:
   - Emotional/relational/personal concern (stress, relationship, family, loneliness) → respond to that reality, NOT a clinical framework
   - Physical symptoms → respond with appropriate medical awareness
   - Mixed (emotional + physical) → address both

3. observed_pattern — Write like a caring knowledgeable friend summarizing what they understand about this specific person. Reference their actual situation. Warm and clear — NOT medical report language.

4. severity:
   - "mild" → emotional issues, lifestyle concerns, minor symptoms
   - "moderate" → physical symptoms needing attention, long-term issues
   - "high" → genuinely serious symptoms only

5. care_recommendation — The single most useful, specific thing for THIS person. Use their context. Personal, actionable.

6. precautions — 2 genuinely relevant precautions for their actual situation:
   - Emotional issue → emotional/relational precautions
   - Physical issue → relevant physical precautions
   - NOT generic, NOT copy-paste

7. consult_specialist — ONLY for genuine medical need:
   - Emotional/personal/relationship issues → empty array
   - Mild lifestyle issues → empty array
   - Actual physical symptoms needing a specialist → appropriate specialist

8. suggested_tests — ONLY if clinically clear reason exists:
   - Emotional/personal issues → empty array
   - Heart history + chest symptoms → Echocardiogram, relevant cardiac tests
   - DO NOT suggest "Basic Health Checkup" or "Blood Sugar Test" for emotional concerns

9. home_relief — 2 specific, SAFE, relevant suggestions:
   - For cardiac/heart patients → NO massage, NO physical strain suggestions
   - For emotional issues → practical emotional relief (journaling, talking to someone, etc.)
   - For physical symptoms → safe, appropriate home remedies
   - NEVER suggest anything that could be unsafe for their specific condition

10. thought — Short, warm, personal closing insight. Reference their actual situation. Not generic.

STYLE QUALITY:
- Keep every field concise and premium: 1-2 short sentences only.
- Be realistic and useful, not generic. Every answer must connect to the user's actual symptoms, duration, lifestyle, stress context, red flags, or medical background.
- Never frighten the user. Use calm, motivating language that helps them improve and take the right next step.
- Never diagnose, prescribe medicine, guarantee recovery, or claim certainty.
- Avoid vague lines like "take care of your health" unless paired with a concrete action the user can do today.
- In Hindi/Hinglish, avoid repetitive openings like "aaj kal..." and avoid overly casual wording like "tumhe/tumhara"; use respectful, friendly "aapko/aapke" unless the user is clearly casual first.
- Make the issue and solution understandable in one reading: what may be happening, what to do now, and when to seek professional help.
- No awkward sentence formation, no over-explaining, no long paragraphs.
- Do not repeat the same meaning in multiple fields.
- Do not use dramatic, scary, cheap, robotic, or fake-certain language.
- If the concern is emotional/personal, make the report feel emotionally intelligent and practical, not medicalized.
- If the concern is physical, give careful awareness guidance without diagnosis or prescription.
- Use tests/specialists only when truly relevant from the user's details.

DEEP ANALYSIS RULES:
- First infer the main category: physical, emotional, lifestyle, mixed, or red-flag.
- For emotional or personal issues, focus on emotional clarity, sleep, communication, grounding, support, and safety. Do not medicalize normal stress.
- For physical symptoms, explain likely body signals carefully without diagnosis, then give safe home steps and clear consultation triggers.
- For mixed issues, mention both body and mind in a balanced way.
- If red_flag is not "No", keep tone calm but prioritize qualified medical care promptly.
- If the user's detail is vague, give observation steps and one useful follow-up direction inside care_recommendation.

LANGUAGE:
- Hinglish: warm Hindi-English mix, simple, natural — like an educated Indian friend
- Hindi: simple conversational Hindi, easy to understand
- English: warm, simple, like a caring friend
- Use the person's name lightly only when it feels respectful. For age 45 or above, avoid first-name style addressing and use a mature respectful tone such as "aap/you".
- Do not overuse the name in multiple fields.
- NEVER clinical/robotic language

OUTPUT: Return ONLY valid JSON — no preamble, no markdown, nothing else.

{
  "observed_pattern": "warm personal summary using their name and actual situation",
  "severity": "mild | moderate | high",
  "care_recommendation": "most useful specific personal guidance",
  "precautions": ["relevant precaution 1", "relevant precaution 2"],
  "consult_specialist": ["only if genuinely medically needed, else empty array"],
  "suggested_tests": ["only if clinically relevant and safe, else empty array"],
  "home_relief": ["safe specific helpful thing 1", "safe specific helpful thing 2"],
  "thought": "short warm personal closing insight"
}"""


def build_report_user_message(symptoms: str, profile: dict) -> str:
    if not profile:
        return symptoms

    name           = profile.get("name", "")
    age            = profile.get("age", "")
    gender         = profile.get("gender", "")
    location       = profile.get("location", "")
    disease        = profile.get("disease", "no")
    disease_detail = profile.get("disease_detail", "")
    duration       = profile.get("duration", "")
    pain           = profile.get("pain", "")
    sleep          = profile.get("sleep", "")
    exercise       = profile.get("exercise", "")
    water          = profile.get("water_intake", "")
    weight         = profile.get("weight", "")
    height_cm      = profile.get("height_cm", "")
    concern_type   = profile.get("concern_type", "")
    red_flag       = profile.get("red_flag", "")
    food_pattern   = profile.get("food_pattern", "")
    stress_context = profile.get("stress_context", "")
    medicines      = profile.get("medicines", "")

    parts = []
    if name:     parts.append(f"Name: {name}")
    if age:      parts.append(f"Age: {age}")
    if gender:   parts.append(f"Gender: {gender}")
    if location: parts.append(f"Location: {location}")

    if disease == "yes" and disease_detail:
        parts.append(f"Past medical condition: {disease_detail}")
    else:
        parts.append("No known past medical conditions")

    parts.append(f"Current problem / what they shared: {symptoms}")

    if duration: parts.append(f"Duration: {duration}")
    if pain:     parts.append(f"Pain/discomfort level: {pain}")
    if weight:   parts.append(f"Weight: {weight} kg")
    if height_cm: parts.append(f"Height: {height_cm} cm")
    if concern_type: parts.append(f"Main concern type: {concern_type}")
    if red_flag: parts.append(f"Red flag selected: {red_flag}")
    if sleep:    parts.append(f"Sleep: {sleep}")
    if exercise: parts.append(f"Physical activity: {exercise}")
    if water:    parts.append(f"Water intake: {water}")
    if food_pattern: parts.append(f"Food pattern: {food_pattern}")
    if stress_context: parts.append(f"Stress/emotional context: {stress_context}")
    if medicines: parts.append(f"Current medicines: {medicines}")

    return "\n".join(parts)


def parse_json(text: str):
    try:
        text = re.sub(r'```(?:json)?|```', '', text).strip()
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            return json.loads(match.group())
    except Exception as e:
        print("JSON Parse Error:", e)
    return {
        "observed_pattern": "Unable to fully analyze right now.",
        "severity": "mild",
        "care_recommendation": "Please try again with more detail.",
        "precautions": [],
        "consult_specialist": [],
        "suggested_tests": [],
        "home_relief": [],
        "thought": "Small steps taken today lead to better health tomorrow.",
    }


def _short_text(value, fallback="", max_chars=230):
    text = str(value or fallback or "").strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"^(it seems like|lagta hai ki)\s+", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(aaj\s*kal|aj\s*kal)\b[:,]?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(tumhe|tumko)\b", "aapko", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(tumhara|tumhari|tumhare)\b", "aapke", text, flags=re.IGNORECASE)
    if len(text) > max_chars:
        text = text[:max_chars].rsplit(" ", 1)[0].rstrip(".,;") + "."
    return text


def _short_list(value, limit=2):
    if not isinstance(value, list):
        return []
    cleaned = []
    for item in value:
        item = _short_text(item, max_chars=120)
        if item and item not in cleaned:
            cleaned.append(item)
        if len(cleaned) >= limit:
            break
    return cleaned


def _filter_unsafe_relief(items, text_blob):
    if not items:
        return []
    heart_context = any(w in text_blob for w in [
        "heart", "cardiac", "chest pain", "chest tightness", "seena", "saans",
        "breathing difficulty"
    ])
    if not heart_context:
        return items
    unsafe = ["massage", "press", "pressure", "strain", "exercise", "workout", "run"]
    return [item for item in items if not any(word in item.lower() for word in unsafe)]


def _respectful_report_text(text, profile):
    name = str((profile or {}).get("name") or "").strip()
    try:
        age = int(float(str((profile or {}).get("age") or "0").strip() or 0))
    except ValueError:
        age = 0
    if age < 45 or not name or not text:
        return text
    cleaned = re.sub(rf"\b{re.escape(name)}\b,?\s*", "", text, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" ,")
    if cleaned and cleaned[0].islower():
        cleaned = cleaned[0].upper() + cleaned[1:]
    return cleaned or text


def normalize_report_data(data, user_input="", profile=None):
    profile = profile or {}
    if not isinstance(data, dict):
        data = {}

    text_blob = " ".join([
        user_input or "",
        profile.get("concern_type", ""),
        profile.get("stress_context", ""),
        profile.get("symptoms", ""),
    ]).lower()
    emotional = any(w in text_blob for w in [
        "stress", "tension", "anxiety", "overthinking", "relationship", "family",
        "lonely", "sad", "breakup", "husband", "wife", "mental", "emotional"
    ])
    red_flag = str(profile.get("red_flag", "No")).lower()

    observed = _short_text(
        data.get("observed_pattern"),
        "Your details suggest a wellness concern that needs calm observation and small practical steps."
    )
    observed = _respectful_report_text(observed, profile)
    care = _short_text(
        data.get("care_recommendation"),
        "Focus on rest, hydration, and tracking how your symptoms change today."
    )
    care = _respectful_report_text(care, profile)
    severity = str(data.get("severity") or "mild").strip().lower()
    if severity not in {"mild", "moderate", "high"}:
        severity = "mild"
    if red_flag and red_flag != "no":
        severity = "high"
        care = "Because you selected a red-flag symptom, seek qualified medical help promptly instead of relying on home care."
    elif emotional:
        severity = "mild"

    precautions = _short_list(data.get("precautions"), 2) or [
        "Track changes calmly for the next 24 hours.",
        "Avoid self-medicating without professional advice."
    ]
    consultation = _short_list(data.get("consult_specialist"), 2)
    tests = _short_list(data.get("suggested_tests"), 2)
    if emotional and red_flag in {"", "no"}:
        consultation = []
        tests = []

    relief = _short_list(data.get("home_relief"), 2) or [
        "Drink water slowly and take a short rest.",
        "Keep the next meal light and simple if your body feels unsettled."
    ]
    relief = _filter_unsafe_relief(relief, text_blob)
    if not relief:
        relief = [
            "Rest in a comfortable position and avoid exertion.",
            "Arrange qualified medical guidance promptly if symptoms feel severe or unusual."
        ]
    thought = _short_text(
        data.get("thought"),
        "Small, consistent care today can make your next step clearer.",
        max_chars=150
    )
    thought = _respectful_report_text(thought, profile)

    return {
        "observed_pattern": observed,
        "severity": severity,
        "care_recommendation": care,
        "precautions": precautions,
        "consult_specialist": consultation,
        "suggested_tests": tests,
        "home_relief": relief,
        "thought": thought,
    }


def ai_health_response(user_input: str, history: list = None, profile: dict = None) -> dict:
    if not USE_AI_ASSISTANT or not AI_AVAILABLE:
        return None

    full_message = build_report_user_message(user_input, profile)

    # Language detection
    lang = detect_language(user_input)
    if lang == "english" and profile:
        for field in ("disease_detail", "name"):
            val = profile.get(field, "")
            if val:
                l = detect_language(val)
                if l != "english":
                    lang = l
                    break

    lang_instruction = {
        "hinglish": "Respond in natural Hinglish — warm Hindi-English mix, like an educated Indian friend. Simple and easy to understand.",
        "hindi":    "Respond in simple conversational Hindi — warm, easy words, not formal.",
        "english":  "Respond in simple warm English — like a caring knowledgeable friend.",
    }.get(lang, "Respond in simple English.")

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=550,
            timeout=20,
            messages=[
                {"role": "system", "content": REPORT_SYSTEM_PROMPT},
                {"role": "system", "content": lang_instruction},
                {"role": "user",   "content": full_message},
            ]
        )
        raw = response.choices[0].message.content.strip()
        return normalize_report_data(parse_json(raw), user_input, profile)

    except Exception as e:
        print("Report AI error:", e)
        return None


# =========================================================
# ONBOARDING AI
# =========================================================
def generate_onboarding_summary(answers: dict) -> dict:
    if not USE_AI_ASSISTANT or not AI_AVAILABLE:
        return {
            "archetype": "The Resilient Explorer",
            "archetype_subtitle": "You are navigating your health journey steadily.",
            "insights": [
                "You are showing great awareness by checking in.",
                "Small, consistent steps today lead to better energy tomorrow.",
                "Prioritize one small recovery habit tonight."
            ]
        }
        
    system_prompt = """You are a premium behavioral psychologist AI for Healthify.
Your task is to analyze the user's 6 onboarding answers and generate a powerful, memorable, 3-bullet-point summary.
Output strictly in JSON format.

RULES:
- Maximum 3 bullet points.
- Maximum 60 words total across all bullets.
- Never use "As an AI", "Based on your answers", "I recommend", or medical terms.
- Use deep behavioral insights (e.g. "You don't appear unhealthy. You appear overloaded.").
- Keep it punchy, premium, and emotionally rewarding.

JSON FORMAT:
{
  "archetype": "The Overloaded Performer", 
  "archetype_subtitle": "You tend to keep moving forward even when recovery should come first.",
  "insights": [
    "Insight 1",
    "Insight 2",
    "Insight 3"
  ]
}"""
    
    user_content = json.dumps(answers)
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0.4,
            max_tokens=200,
            timeout=10,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ]
        )
        raw = response.choices[0].message.content.strip()
        data = parse_json(raw)
        
        if not data.get("insights") or len(data.get("insights", [])) == 0:
            raise ValueError("No insights generated")
            
        return {
            "archetype": data.get("archetype", "The Focused Explorer"),
            "archetype_subtitle": data.get("archetype_subtitle", "You are navigating your health with intention."),
            "insights": data.get("insights")[:3]
        }
    except Exception as e:
        print("Onboarding AI error:", e)
        return {
            "archetype": "The Resilient Explorer",
            "archetype_subtitle": "You are navigating your health journey steadily.",
            "insights": [
                "You are showing great awareness by checking in.",
                "Small, consistent steps today lead to better energy tomorrow.",
                "Prioritize one small recovery habit tonight."
            ]
        }
