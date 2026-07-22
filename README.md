# Healthify 🌿
A premium wellness companion that gamifies your health journey. Built during the OpenAI Build Week!

## 🚀 What it does
- **MindCare AI:** A chatbot that actually understands your emotional and physical symptoms and gives empathetic advice.
- **Quick Health Score:** Check your daily health score and get some actionable recovery steps.
- **Habit Builder:** A 21-day tracker to help you build healthy routines.
- **Full Health Report:** Get a full analysis of your metrics and download it as a clean PDF.
- **Healthify Games:** Cognitive exercises like Memory Match.

---

## 🧠 How I used Codex & GPT-5.6

Building this full-stack responsive web app in just one week was really hard. I heavily relied on the OpenAI ecosystem to make it work:

### 🛠️ Codex (My Pair Programmer)
Codex was amazing for accelerating the development. I used it to:
- Scaffold the Python Flask backend and API routing.
- Integrate the Supabase authentication securely.
- Safely inject complex CSS styling (like the glassmorphism UI) without breaking my existing grids.
- Write the logic for generating the downloadable PDF reports.

### 💡 GPT-5.6 (The Brain)
To make Healthify feel like a true companion, I engineered the logic using GPT-5.6:
- Designed the core prompt architecture and personality for the MindCare AI.
- Setup strict psychological and medical safety guardrails so the AI responds safely and detects emergencies.
- *Note: To ensure fast responses on the live web demo (and avoid API limits), these GPT-5.6 engineered prompts are being executed on a Groq backend.*

---

## 🔑 Codex Session IDs
Here are the feedback session IDs where the majority of the core functionality was built. 
- `019f79e0-61e1-7723-a864-e3b05e2807d5`
- `019e6980-9b34-7a42-b86f-e2ad228a2d24`
- `019efa04-363c-79f0-a8c7-2001ed133f4c`

---

## 💻 How to Test & Run (For Judges)

### 1. Live Web Demo (Easiest Method)
You don't need to install anything! Just visit the live app here:
🔗 **[Live Demo](https://healthify-uxwh.onrender.com)**
- Click on **"Continue as Guest"** for instant access to the Dashboard.

### 2. Local Setup
If you want to run the app locally on your machine:

1. **Clone the repo:**
   ```bash
   git clone https://github.com/amittiw-developer/Healthify.git
   cd Healthify
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app:**
   ```bash
   python app.py
   ```
   The app will run at `http://localhost:5000`.

---
*Built with ❤️ for the OpenAI Build Week Thanks for reading!*
