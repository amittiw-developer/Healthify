GROUPS = {
    "viral":["fever","body_pain","fatigue","headache"],
    "eye_strain":["eye_burning","headache"],
    "gastric":["nausea","back_pain"],
    "muscle_strain":["back_pain","body_pain"]
}

def detect_conditions(symptoms):

    scores={}

    for group,items in GROUPS.items():
        score=len(set(symptoms)&set(items))
        if score>0:
            scores[group]=score

    # top 2 only
    return sorted(scores,key=scores.get,reverse=True)[:2]
