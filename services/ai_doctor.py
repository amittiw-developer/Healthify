from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are a friendly health assistant, not a doctor.

Rules:
- No disease diagnosis
- No scary words
- Simple explanation
- Give daily care advice
- Use Hinglish if user uses Hinglish
- Human caring tone
- Short response

Answer format:
1) Body signal
2) Why happening
3) What to do today
4) When to see doctor (only if needed)
"""

def ask_health_ai(symptoms: str):

    completion = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        temperature=0.4,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": symptoms}
        ]
    )

    return completion.choices[0].message.content