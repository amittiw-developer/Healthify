# services/report_builder.py

import re


# ---------------------------------------------------
# TEXT HELPERS
# ---------------------------------------------------

def safe(text, default=""):
    if not text:
        return default
    text = str(text).strip()
    return text[0].upper() + text[1:] if text else default


def join(items):
    if not items:
        return ""
    return ", ".join([str(i).strip() for i in items if str(i).strip()])


# ---------------------------------------------------
# SEVERITY LANGUAGE (HUMAN DOCTOR STYLE)
# ---------------------------------------------------

def severity_sentence(level):

    level = level.lower()

    if "critical" in level:
        return "This situation may require emergency medical care."
    if "urgent" in level:
        return "This should be medically checked today."
    if "high" in level:
        return "A doctor consultation is strongly recommended."
    if "moderate" in level:
        return "Medical attention is advisable if symptoms continue."
    return "Basic care and observation is usually sufficient."


# ---------------------------------------------------
# REASSURANCE CONTROL (NEVER MISLEAD)
# ---------------------------------------------------

def reassurance_text(level):

    level = level.lower()

    if any(w in level for w in ["critical","urgent","high"]):
        return "Do not ignore these symptoms. Timely medical evaluation is important."

    return "At present it does not strongly suggest a dangerous condition, but monitoring is recommended."


# ---------------------------------------------------
# SPECIALIST FORMAT
# ---------------------------------------------------

def specialist_format(items):
    if not items:
        return "<b>General Physician</b>"
    return f"<b>{items[0]}</b>"


# ---------------------------------------------------
# HEART PATIENT SAFETY OVERRIDE
# ---------------------------------------------------

CARDIAC_HISTORY = [
    "valve replacement","bypass","stent","angioplasty","pacemaker","heart surgery","open heart"
]

CARDIAC_SIGNS = [
    "chest pain","left chest","pressure chest","tightness","breath","sweating","radiating"
]


def force_cardiac_severity(symptoms, severity):

    text = (symptoms + " " + severity).lower()

    if any(h in text for h in CARDIAC_HISTORY) and any(s in text for s in CARDIAC_SIGNS):
        return "Critical"

    return severity


# ---------------------------------------------------
# MAIN REPORT BUILDER
# ---------------------------------------------------

def build_human_report(user_data: dict, ai_data: dict):

    symptoms = safe(user_data.get("symptoms"), "general discomfort")
    duration = safe(user_data.get("duration"), "recent onset")
    pain = safe(user_data.get("pain"), "mild")

    observed = safe(ai_data.get("observed_pattern"), "body stress response")
    care = safe(ai_data.get("care_recommendation"), "rest and hydration")

    tests = join(ai_data.get("suggested_tests"))
    relief = join(ai_data.get("home_relief"))
    specialists = ai_data.get("consult_specialist", [])

    # ---------------- SEVERITY ----------------
    severity = safe(ai_data.get("severity"), "Moderate")
    severity = force_cardiac_severity(symptoms, severity)

    severity_line = severity_sentence(severity)
    reassurance = reassurance_text(severity)

    doctor_name = specialist_format(specialists)

    # ---------------- REPORT TEXT ----------------

    complaint = (
        f"You reported {symptoms} for {duration}. "
        f"The discomfort level described is {pain.lower()}."
    )

    interpretation = (
        f"The pattern of symptoms suggests {observed}. "
        f"It helps to monitor how it changes over time."
    )

    action = (
        f"Immediate step: {care} "
        f"Avoid strain for now."
    )

    monitor = (
        "Watch for warning signs like increasing pain, breathing difficulty, dizziness, sweating, or reduced activity tolerance."
    )

    today_plan = (
        f"For today: maintain hydration and light meals. "
        f"{relief if relief else 'Give your body adequate rest.'}"
    )

    doctor = (
        f"If symptoms continue or worsen, consult {doctor_name}. "
        + (f"Tests that may be useful: {tests}." if tests else "")
    )

    recovery = (
        "Recovery depends on the cause and response to care."
    )

    habit = (
        "Take short rest breaks and avoid overexertion."
    )

    # ---------------- RETURN STRUCTURE ----------------
    return {
        "severity": severity_line,
        "complaint_summary": complaint,
        "body_interpretation": interpretation,
        "what_to_do": action,
        "monitor_for": monitor,
        "care_plan": today_plan,
        "doctor_guidance": doctor,
        "recovery_expectation": recovery,
        "home_care": habit,
        "reassurance": reassurance
    }