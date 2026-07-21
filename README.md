# Healthify 🌿
A premium, AI-driven wellness companion that gamifies your health journey, built during the OpenAI Build Week.

## 🚀 Features
- **MindCare AI:** A conversational AI that understands your emotional and physical symptoms and provides personalized, empathetic advice.
- **Quick Health Score:** Gamified daily health tracking with actionable recovery steps.
- **Habit Builder:** A 21-day tracker to help you build and maintain healthy routines.
- **Full Health Report:** Get a comprehensive analysis of your metrics and download it as a clean PDF with one click.
- **Healthify Games:** Cognitive exercises like Memory Match to keep your brain sharp.

---

## 🧠 How We Used Codex & GPT-5.6

Building a full-stack, responsive wellness application with 30+ pages in one week was a monumental task. This project heavily relied on the OpenAI ecosystem:

### 🛠️ Codex (The Ultimate Pair Programmer)
Codex was instrumental in accelerating the development process. We used it to:
- Scaffold the complex Python Flask backend and API routing.
- Integrate the Supabase authentication and database connection securely.
- Safely inject and debug complex CSS styling (like glassmorphism) without breaking the existing UI grid.
- Write the logic for generating the downloadable PDF health reports.

### 💡 GPT-5.6 (The Brain)
To ensure Healthify felt like a true companion, we engineered the logic using GPT-5.6:
- Designed the core prompt architecture and personality for **MindCare AI**.
- Established strict psychological and medical safety guardrails to ensure the AI responds empathetically and safely detects emergencies.
- *Note: To ensure lightning-fast responses on our live web demo without API rate limits, these GPT-5.6 engineered prompts are being executed on a fast Groq backend.*

---

## 🔑 Codex Session IDs
Here are the feedback session IDs where the majority of the core functionality was built:
- `019f79e0-61e1-7723-a864-e3b05e2807d5`
- `019e6980-9b34-7a42-b86f-e2ad228a2d24`
- `019efa04-363c-79f0-a8c7-2001ed133f4c`

---

## 💻 How to Test & Run

### 1. Live Web Demo (Easiest Method)
You don't need to install anything! Just visit our live app:
🔗 **[Live Demo](https://healthify-uxwh.onrender.com)**
- Click on **"Continue as Guest"** for instant access to the Dashboard.
- Try exploring MindCare AI, updating your Profile, or generating a Health Report!

### 2. Local Setup Instructions
If you wish to run the app locally on your machine:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/healthify.git
   cd healthify
   ```

2. **Install dependencies:**
   Make sure you have Python installed, then run:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables:**
   Create a `.env` file in the root directory and add your Supabase and Groq keys:
   ```
   GROQ_API_KEY=your_groq_key
   SUPABASE_URL=your_supabase_url
   SUPABASE_ANON_KEY=your_supabase_anon_key
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```
   The app will be available at `http://localhost:5000`.

---
*Built with ❤️ for the OpenAI Build Week.*
