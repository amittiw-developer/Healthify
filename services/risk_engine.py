import random

def calculate_health_score(age, sleep, water, activity, symptoms, symptom_detail):

    score = 100
    reasons = []

    # AGE IMPACT
    age = int(age)
    if age >= 75:
        score -= 25
        reasons.append("advanced age recovery slower")
    elif age >= 60:
        score -= 18
        reasons.append("senior age factor")
    elif age >= 45:
        score -= 10
        reasons.append("mid age metabolism change")

    # SLEEP
    sleep = float(sleep)
    if sleep < 6:
        score -= 18
        reasons.append("sleep debt affecting immunity")
    elif sleep < 7:
        score -= 10
        reasons.append("insufficient recovery sleep")

    # WATER
    water = float(water)
    if water < 2:
        score -= 12
        reasons.append("low hydration level")
    elif water < 3:
        score -= 5
        reasons.append("mild dehydration risk")

    # ACTIVITY
    if activity == "low":
        score -= 15
        reasons.append("low physical activity")
    elif activity == "medium":
        score -= 5
        reasons.append("moderate activity")

    # SYMPTOMS
    symptom_detail = symptom_detail.lower()

    if symptoms == "yes" and symptom_detail:
        score -= 15

        if any(x in symptom_detail for x in ["fever","bukhar"]):
            reasons.append("possible infection signs")

        elif any(x in symptom_detail for x in ["headache","sir dard"]):
            reasons.append("stress or dehydration symptom")

        elif any(x in symptom_detail for x in ["stomach","pet","gas","acidity"]):
            reasons.append("digestive disturbance")

        elif any(x in symptom_detail for x in ["weakness","thakan"]):
            reasons.append("fatigue indication")

        else:
            reasons.append("active symptoms reported")

    score = max(5, min(100, score))

    # CONDITION
    if score >= 80:
        condition = "Healthy"
        ai = "Your body is functioning efficiently today."
        motivation = "Great consistency! Keep maintaining this lifestyle."
        fact = "Healthy routines reduce 70% lifestyle diseases risk"

    elif score >= 60:
        condition = "Moderate"
        ai = "Your health is stable but improvements needed."
        motivation = "Small daily habits can significantly improve health."
        fact = "Sleep and hydration improve energy levels within 3 days"

    else:
        condition = "Needs Attention"
        ai = "Your body is under stress today."
        motivation = "Start improving routine today — your future body depends on it."
        fact = "Ignoring symptoms increases illness risk by 3x"

    return {
        "score": score,
        "condition": condition,
        "reasons": reasons,
        "ai_message": ai,
        "motivation": motivation,
        "health_fact": fact
    }
