# services/language_engine.py

import re


# ---------------- LANGUAGE DETECTION ----------------

def detect_user_language(text: str):
    """
    Returns: 'hindi', 'hinglish', 'english'
    """

    if not text:
        return "english"

    text_low = text.lower()

    # Pure Hindi (Unicode detection)
    if re.search(r'[\u0900-\u097F]', text_low):
        return "hindi"

    # Hinglish detection keywords
    hinglish_words = [
        "hai","nahi","kyu","kya","kaise","kab","mujhe","mere","mera",
        "ho raha","lag raha","dard","bukhar","sardi","khansi","pet",
        "sar","chakkar","jalan","thakan","kamjori","saans","ghabrahat",
        "ulta","ulti","soya","soyi","uthte","baithte","khane","peene"
    ]

    score = sum(1 for w in hinglish_words if w in text_low)

    if score >= 2:
        return "hinglish"

    return "english"


# ---------------- TONE PROFILES ----------------

def tone_pack(language: str):
    """
    Returns tone style dictionary used by report builder
    """

    if language == "hindi":
        return {
            "care_word": "dhyaan rakhein",
            "doctor_word": "doctor se milna sahi rahega",
            "rest_word": "aaram dein",
            "normal_word": "ye aam taur par theek ho jata hai"
        }

    if language == "hinglish":
        return {
            "care_word": "thoda care karein",
            "doctor_word": "doctor consult kar lena better rahega",
            "rest_word": "rest dein",
            "normal_word": "usually ye theek ho jata hai"
        }

    # english default
    return {
        "care_word": "take care",
        "doctor_word": "medical consultation would be appropriate",
        "rest_word": "give it proper rest",
        "normal_word": "this usually improves naturally"
    }