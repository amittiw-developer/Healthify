from flask import Flask, request, jsonify, render_template, session, redirect, send_file, url_for
from datetime import datetime, timedelta
import pytz
import uuid
import os
import logging
import re
from markupsafe import escape

from db import db
try:
    from flask_migrate import Migrate
except ImportError:
    Migrate = None
from config import Config

from models import User, Report
from auth_supabase import send_otp, verify_otp, google_login

from services.health_engine import (
    suggest_tests,
    random_precautions,
    random_consultations
)

from services.pdf_service import generate_pdf
from services.risk_engine import calculate_health_score
from services.symptom_engine import build_response

from services.ai_bridge import ai_health_response, ai_chat_response


# =========================================================
# APP INIT
# =========================================================
HealthiFy = Flask(__name__)
HealthiFy.config.from_object(Config)
HealthiFy.secret_key = HealthiFy.config.get("SECRET_KEY") or os.getenv(
    "SECRET_KEY",
    "change-this-secret-key"
)

db.init_app(HealthiFy)
migrate = Migrate(HealthiFy, db) if Migrate else None

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

logging.basicConfig(level=logging.INFO)


@HealthiFy.after_request
def add_security_headers(response):
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    response.headers.setdefault("Cache-Control", "no-store")
    return response


# =========================================================
# HELPERS
# =========================================================
def safe(value, default=""):
    if value is None:
        return default
    value = str(value).strip()
    return value if value else default


def auth_setup_message():
    return (
        "Supabase auth is not ready. Check SUPABASE_URL, SUPABASE_ANON_KEY, "
        "Email OTP provider, Google provider, and redirect URL http://127.0.0.1:5001/google-complete."
    )


def generate_report_id():
    now    = datetime.now().strftime("%Y%m%d%H%M%S")
    unique = uuid.uuid4().hex[:6].upper()
    return f"HF-{now}-{unique}"


def login_required(view):
    def wrapped(*args, **kwargs):
        if 'user' not in session:
            return redirect('/login')
        return view(*args, **kwargs)

    wrapped.__name__ = view.__name__
    return wrapped


# =========================================================
# ROOT
# =========================================================
@HealthiFy.route('/')
def branding():
    return render_template('branding.html')


# =========================================================
# AUTH
# =========================================================
@HealthiFy.route('/login')
def login():
    if 'user' in session:
        return redirect('/home')
    return render_template('login.html')


@HealthiFy.route('/login-password', methods=['POST'])
def login_password():
    email = safe(request.form.get("email"))
    password = request.form.get("password", "")
    if not email or not password:
        return render_template('login.html', error="Please enter email and password.")
    try:
        from auth import login_user
        user = login_user(email, password)
        if user:
            session.clear()
            session['user'] = email
            session['is_guest'] = False
            session['profile'] = {
                "name": user.get("name", ""),
                "email": email,
                "avatar": "pulse"
            }
            return render_template('login.html', success="Signed in successfully.", redirect_to="/onboarding")
    except Exception:
        logging.exception("Password login error")
    return render_template('login.html', error="Login failed. Use OTP, Google, or guest access.")


@HealthiFy.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        if 'user' in session:
            return redirect('/home')
        return render_template('signup.html')

    email = safe(request.form.get("email"))
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not email or not password:
        return render_template('signup.html', error="Email and password are required.")
    if password != confirm_password:
        return render_template('signup.html', error="Passwords do not match.")
    if len(password) < 6:
        return render_template('signup.html', error="Use at least 6 characters for password.")

    session['signup_email'] = email
    session['signup_password_set'] = True
    try:
        send_otp(email)
        session['temp_email'] = email
        return render_template("verify_otp.html")
    except Exception:
        logging.exception("Signup OTP error")
        return render_template('signup.html', error="OTP service is not configured. Check Supabase settings.")


@HealthiFy.route('/signup-send-otp', methods=['POST'])
def signup_send_otp():
    data = request.get_json(silent=True) or request.form.to_dict()
    email = safe(data.get("email")).lower()
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        return jsonify({"status": "error", "message": "Enter a valid email address."}), 400
    try:
        send_otp(email)
        session['pending_signup_email'] = email
        session['pending_signup_verified'] = False
        return jsonify({"status": "ok", "message": "OTP sent to your email."})
    except Exception as exc:
        logging.exception("Signup OTP send error")
        return jsonify({"status": "error", "message": f"{auth_setup_message()} Details: {safe(exc, 'configuration error')}"}), 503


@HealthiFy.route('/signup-verify-otp', methods=['POST'])
def signup_verify_otp():
    data = request.get_json(silent=True) or request.form.to_dict()
    email = session.get('pending_signup_email')
    otp = safe(data.get("otp"))
    if not email or not otp:
        return jsonify({"status": "error", "message": "OTP details missing."}), 400
    try:
        if verify_otp(email, otp):
            session['pending_signup_verified'] = True
            return jsonify({"status": "ok", "message": "Email verified successfully."})
    except Exception:
        logging.exception("Signup OTP verify error")
    return jsonify({"status": "error", "message": "Invalid OTP. Please try again."}), 400


@HealthiFy.route('/create-account', methods=['POST'])
def create_account():
    data = request.get_json(silent=True) or request.form.to_dict()
    email = session.get('pending_signup_email')
    password = data.get("password", "")
    confirm_password = data.get("confirm_password", "")
    if not session.get('pending_signup_verified') or not email:
        return jsonify({"status": "error", "message": "Please verify your email first."}), 400
    if password != confirm_password:
        return jsonify({"status": "error", "message": "Passwords do not match."}), 400
    if len(password) < 8:
        return jsonify({"status": "error", "message": "Use at least 8 characters for better security."}), 400
    try:
        from auth import create_user
        create_user(email.split("@")[0], email, password)
    except Exception:
        logging.exception("Create account table insert error")
        return jsonify({"status": "error", "message": "Account table is not ready. Check Supabase users table configuration."}), 503
    session.pop('pending_signup_email', None)
    session.pop('pending_signup_verified', None)
    return jsonify({"status": "ok", "message": "Account created. Login with email and password."})


@HealthiFy.route('/forgot-details')
def forgot_details():
    return render_template('forgot_details.html')


@HealthiFy.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return render_template('admin_login.html')

    username = safe(request.form.get("username"))
    password = request.form.get("password", "")
    if username == "admin" and password == "admin":
        session.clear()
        session['user'] = "Healthify Admin"
        session['is_guest'] = False
        session['is_admin'] = True
        session['profile'] = {"name": "Healthify Admin", "email": "admin@healthify.local", "avatar": "shield"}
        return render_template('admin_login.html', success="Admin access granted.", redirect_to="/onboarding")
    return render_template('admin_login.html', error="Invalid admin credentials.")


@HealthiFy.route('/google-login')
def google_login_route():
    try:
        response = google_login(url_for("google_complete", _external=True))
        if hasattr(response, "url"):
            return redirect(response.url)
        return render_template('login.html', error=auth_setup_message())
    except Exception as exc:
        logging.exception("Google login error")
        return render_template('login.html', error=f"{auth_setup_message()} Details: {safe(exc, 'configuration error')}")


@HealthiFy.route('/google-complete')
def google_complete():
    email = safe(request.args.get("email"))
    name = safe(request.args.get("name"))
    code = request.args.get("code")
    if code:
        try:
            client = __import__("supabase_client").require_supabase()
            auth = getattr(client, "auth", None)
            if auth and hasattr(auth, "exchange_code_for_session"):
                result = auth.exchange_code_for_session({"auth_code": code, "redirect_to": url_for("google_complete", _external=True)})
                user = getattr(result, "user", None) or getattr(getattr(result, "session", None), "user", None)
                meta = getattr(user, "user_metadata", {}) or {}
                email = email or safe(getattr(user, "email", "") or meta.get("email"))
                name = name or safe(meta.get("full_name") or meta.get("name") or meta.get("display_name"))
        except Exception:
            logging.exception("Google callback profile extraction failed")
    if not email:
        email = safe(request.args.get("user_email"))
    if not name and email:
        name = email.split("@")[0].replace(".", " ").replace("_", " ").title()
    if email or name:
        name = name or "Healthify User"
        session.clear()
        session['user'] = email or name
        session['is_guest'] = False
        session['profile'] = {"name": name, "email": email, "avatar": "pulse", "login_provider": "google"}
        return render_template('login.html', success="Google sign-in completed.", redirect_to="/onboarding")
    return render_template('google_complete.html')


@HealthiFy.route('/google-profile-sync', methods=['POST'])
def google_profile_sync():
    data = request.get_json(silent=True) or {}
    access_token = safe(data.get("access_token"))
    refresh_token = safe(data.get("refresh_token"))
    email = ""
    name = ""
    try:
        client = __import__("supabase_client").require_supabase()
        auth = getattr(client, "auth", None)
        result = auth.set_session(access_token, refresh_token) if access_token and refresh_token else None
        user = getattr(result, "user", None) or getattr(getattr(result, "session", None), "user", None)
        if not user and access_token:
            user_resp = auth.get_user(access_token)
            user = getattr(user_resp, "user", None)
        meta = getattr(user, "user_metadata", {}) or {}
        email = safe(getattr(user, "email", "") or meta.get("email"))
        name = safe(meta.get("full_name") or meta.get("name") or meta.get("display_name"))
    except Exception:
        logging.exception("Google profile sync failed")
    if not email:
        return jsonify({"status": "error", "message": "Google profile could not be verified."}), 400
    if not name:
        name = email.split("@")[0].replace(".", " ").replace("_", " ").title()
    session.clear()
    session['user'] = email
    session['is_guest'] = False
    session['profile'] = {"name": name, "email": email, "avatar": "pulse", "login_provider": "google"}
    return jsonify({"status": "ok", "redirect": "/onboarding", "profile": session['profile']})


@HealthiFy.route('/send-otp', methods=['POST'])
def sendotp():
    email = request.form.get("email")
    if not email:
        return "Email is required", 400
    try:
        send_otp(email)
        session['temp_email'] = email
        return render_template("verify_otp.html")
    except Exception:
        logging.exception("OTP send error")
        return "OTP service is not configured. Please check Supabase settings.", 503


@HealthiFy.route('/verify-otp', methods=['POST'])
def verifyotp():
    otp   = request.form.get("otp")
    email = session.get('temp_email')
    try:
        if email and otp and verify_otp(email, otp):
            session.clear()
            session['user']     = email
            session['is_guest'] = False
            session['profile']  = {"email": email, "avatar": "pulse"}
            return redirect('/onboarding')
    except Exception:
        logging.exception("OTP verify error")
    return "Invalid OTP"


@HealthiFy.route('/guest')
def guest():
    session.clear()
    session['user']     = f"Guest-{uuid.uuid4().hex[:5]}"
    session['is_guest'] = True
    session['profile']  = {"name": session['user'], "avatar": "leaf"}
    return redirect('/onboarding')


@HealthiFy.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# =========================================================
# ONBOARDING
# =========================================================
@HealthiFy.route('/onboarding')
@login_required
def onboarding():
    if session.get('onboarding_complete'):
        return redirect('/home')
    return render_template('onboarding.html')


@HealthiFy.route('/api/onboarding-submit', methods=['POST'])
@login_required
def onboarding_submit():
    data = request.get_json(silent=True) or {}
    answers = data.get("answers", {})
    
    sleep_ans = answers.get("q2", "")
    stress_ans = answers.get("q3", "")
    energy_ans = answers.get("q4", "")
    
    sleep_score = 90 if "8+" in sleep_ans else (60 if "6-7" in sleep_ans else 30)
    stress_score = 20 if "High" in stress_ans else (60 if "Moderate" in stress_ans else 90)
    energy_score = 90 if "High" in energy_ans else (50 if "Average" in energy_ans else 20)
    overall = int((sleep_score + stress_score + energy_score + 70) / 4)
    
    scores = {
        "overall": overall,
        "sleep": sleep_score,
        "stress": stress_score,
        "energy": energy_score,
        "lifestyle": 70
    }
    
    try:
        from services.ai_bridge import generate_onboarding_summary
        ai_result = generate_onboarding_summary(answers)
    except Exception as e:
        import logging
        logging.exception("Onboarding AI generation failed")
        ai_result = {
            "archetype": "The Resilient Explorer",
            "archetype_subtitle": "You are navigating your health journey steadily.",
            "insights": ["Take one small step today for better recovery."]
        }
    
    session['onboarding_complete'] = True
    session['onboarding_scores'] = scores
    
    return jsonify({
        "status": "ok", 
        "scores": scores,
        "archetype": ai_result.get("archetype"),
        "archetype_subtitle": ai_result.get("archetype_subtitle"),
        "insights": ai_result.get("insights")
    })


# =========================================================
# HOME
# =========================================================
@HealthiFy.route('/home')
@login_required
def home():
    return render_template(
        'home.html',
        user=session.get('user'),
        is_guest=session.get('is_guest', False)
    )


# =========================================================
# USER DETAILS
# =========================================================
@HealthiFy.route('/userdetails')
@login_required
def userdetails():
    return render_template('userdetails.html')


@HealthiFy.route('/profile')
@login_required
def profile():
    return render_template('profile.html', profile=session.get('profile', {}))


@HealthiFy.route('/dashboard')
@login_required
def dashboard():
    profile_data = session.get('profile', {})
    health_score = session.get('health_score', {})
    habits = session.get('habits', [])
    games = session.get('game_stats', {})
    checkins = session.get('checkins', [])
    return render_template(
        'dashboard.html',
        profile=profile_data,
        result=health_score,
        habits=habits,
        games=games,
        checkins=checkins
    )


@HealthiFy.route('/habits')
@login_required
def habits():
    return render_template('habits.html', habits=session.get('habits', []))


@HealthiFy.route('/save-habits', methods=['POST'])
@login_required
def save_habits():
    data = request.get_json(silent=True) or {}
    habits_data = data.get("habits", [])
    if not isinstance(habits_data, list):
        habits_data = []
    session['habits'] = habits_data[:12]
    return jsonify({"status": "ok", "habits": session['habits']})


@HealthiFy.route('/games')
@login_required
def games():
    return render_template('games.html')

@HealthiFy.route('/wellness-age')
@login_required
def wellness_age():
    return render_template('wellness_age.html')

@HealthiFy.route('/help-center')
@login_required
def help_center():
    return render_template('help_center.html')


@HealthiFy.route('/save-game-stats', methods=['POST'])
@login_required
def save_game_stats():
    data = request.get_json(silent=True) or {}
    current = session.get('game_stats', {})
    current.update({
        "streak": safe(data.get("streak"), current.get("streak", "0")),
        "plays": safe(data.get("plays"), current.get("plays", "0")),
        "last_played": safe(data.get("last_played"), current.get("last_played", "")),
    })
    session['game_stats'] = current
    return jsonify({"status": "ok", "game_stats": current})


@HealthiFy.route('/save-checkin', methods=['POST'])
@login_required
def save_checkin():
    data = request.get_json(silent=True) or {}
    today = datetime.now().strftime("%Y-%m-%d")
    checkins = session.get("checkins", [])
    already_today = any(item.get("date") == today for item in checkins)
    entry = {
        "date": today,
        "mood": safe(data.get("mood")),
        "energy": safe(data.get("energy")),
        "stress": safe(data.get("stress")),
        "sleep": safe(data.get("sleep")),
        "water": safe(data.get("water")),
    }
    if not already_today:
        checkins.append(entry)
        checkins = checkins[-120:]
        session["checkins"] = checkins

    advice = build_checkin_advice(entry)
    week_start = datetime.now() - timedelta(days=datetime.now().weekday())
    week_dates = {(week_start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)}
    weekly_count = len([item for item in checkins if item.get("date") in week_dates])
    return jsonify({"status": "ok", "already_today": already_today, "advice": advice, "weekly_count": weekly_count, "checkins": checkins})


def build_checkin_advice(entry):
    mood = entry.get("mood", "")
    energy = entry.get("energy", "")
    stress = entry.get("stress", "")
    sleep = entry.get("sleep", "")
    water = entry.get("water", "")
    lines = []
    if mood in ["low", "sad"]:
        lines.append("Aaj mood halka low lag raha hai, isliye apne din ko simple rakho aur kisi trusted person se baat karna helpful ho sakta hai.")
    elif mood in ["good", "great"]:
        lines.append("Aaj mood positive hai, is energy ko ek small healthy action me convert karo.")
    else:
        lines.append("Aaj ka check-in complete ho gaya. Apne body signals ko notice karna itself ek strong healthy step hai.")
    if energy in ["low", "tired"]:
        lines.append("Energy low hai, heavy targets ki jagah hydration, light food, aur short rest ko priority do.")
    if stress in ["high", "very-high"]:
        lines.append("Stress high hai, 3 minutes slow breathing aur one task at a time approach rakho.")
    if sleep in ["poor", "less"]:
        lines.append("Sleep weak thi, aaj caffeine late evening avoid karo aur bedtime screen time reduce karo.")
    if water in ["low"]:
        lines.append("Water intake low hai, next 2 hours me dheere-dheere 2 glass water complete karo.")
    return " ".join(lines[:3])


def profile_aware_report_fallback(symptoms, profile, fallback, emotional_context):
    name = safe(profile.get("name"), "User")
    duration = safe(profile.get("duration"))
    pain = safe(profile.get("pain"))
    concern_type = safe(profile.get("concern_type"))
    red_flag = safe(profile.get("red_flag"), "No")
    sleep = safe(profile.get("sleep"))
    exercise = safe(profile.get("exercise"))
    water = safe(profile.get("water_intake"))
    food = safe(profile.get("food_pattern"))
    stress = safe(profile.get("stress_context"))
    disease = safe(profile.get("disease"))
    disease_detail = safe(profile.get("disease_detail"))

    context_bits = []
    if duration:
        context_bits.append(f"duration: {duration}")
    if pain:
        context_bits.append(f"discomfort: {pain}")
    if concern_type:
        context_bits.append(f"concern type: {concern_type}")
    if disease == "yes" and disease_detail:
        context_bits.append(f"past condition: {disease_detail}")

    if emotional_context:
        summary = (
            f"{name}, your details point more toward stress or emotional load than a routine physical issue."
            if name != "User"
            else "Your details point more toward stress or emotional load than a routine physical issue."
        )
        if stress:
            summary += f" The context you shared about {stress.lower()} is important here."
        care = "Keep the next step simple: speak to one trusted person, reduce pressure for today, and notice whether sleep, appetite, or mood keeps getting worse."
        precautions = [
            "Do not ignore self-harm thoughts, panic-like breathing trouble, or feeling unsafe.",
            "Avoid making major relationship or family decisions while the emotion is at peak intensity."
        ]
        home_relief = [
            "Write the main worry in 3 lines, then write one small action you can take today.",
            "Do 4 slow breaths, drink water, and move to a calmer place before responding to anyone."
        ]
        return summary, "mild", care, precautions, [], [], home_relief, "Emotional clarity usually comes after the body feels a little safer and calmer."

    summary = fallback.get("cause") or "Your symptoms need calm observation and basic supportive care."
    if context_bits:
        summary = f"{summary} Healthify also considered your {', '.join(context_bits[:3])}."

    if red_flag and red_flag.lower() != "no":
        severity = "high"
        care = "Because a red-flag symptom was selected, please consult qualified medical help promptly instead of relying only on home care."
        consultation = random_consultations(symptoms)
        blood_tests = suggest_tests(symptoms)
        home_relief = ["Rest in a safe position and avoid exertion while arranging medical help."]
    else:
        severity = "moderate" if duration in ["More than a week", "Long term"] or pain == "Strong" else "mild"
        care_parts = [fallback.get("solution") or "Rest, hydrate, and observe your symptoms."]
        if sleep and "less" in sleep.lower():
            care_parts.append("Prioritize sleep recovery tonight.")
        if water and ("low" in water.lower() or "1-2" in water.lower()):
            care_parts.append("Increase water slowly through the day.")
        if food and food.lower() != "balanced":
            care_parts.append("Keep meals light and regular.")
        care = " ".join(care_parts[:3])
        consultation = random_consultations(symptoms)
        blood_tests = suggest_tests(symptoms)
        home_relief = [
            "Take proper rest and avoid heavy activity until symptoms settle.",
            "Keep hydration steady and choose simple, light food."
        ]

    precautions = [
        "Do not self-medicate or mix medicines without professional advice.",
        "Track temperature, pain, breathing, and weakness for changes."
    ]
    if exercise in ["None", "Rare"]:
        precautions[1] = "Restart activity gently only after symptoms improve."

    return summary, severity, care, precautions, consultation, blood_tests, home_relief, "Small, timely care makes it easier to decide the right next step."


def build_report_snapshot(profile, severity, emotional_context):
    water = safe(profile.get("water_intake"), "").lower()
    sleep = safe(profile.get("sleep"), "").lower()
    pain = safe(profile.get("pain"), "").lower()
    duration = safe(profile.get("duration"), "").lower()
    food = safe(profile.get("food_pattern"), "").lower()

    hydration = 35
    if "very low" in water:
        hydration = 88
    elif "1-2" in water:
        hydration = 68
    elif "2-3" in water:
        hydration = 42
    elif "good" in water:
        hydration = 24

    rest = 40
    if "less" in sleep or "poor" in sleep:
        rest = 86
    elif "6-7" in sleep:
        rest = 58
    elif "8+" in sleep or "7-8" in sleep:
        rest = 28
    if emotional_context:
        rest = max(rest, 72)

    priority = {"high": 90, "moderate": 64, "mild": 38}.get(str(severity).lower(), 46)
    if "strong" in pain or "long" in duration or "week" in duration:
        priority = max(priority, 72)
    if "irregular" in food or "junk" in food or "low appetite" in food:
        priority = min(95, priority + 8)

    def label(score):
        if score >= 75:
            return "High"
        if score >= 50:
            return "Moderate"
        return "Low"

    return {
        "hydration": hydration,
        "hydration_label": label(hydration),
        "rest": rest,
        "rest_label": label(rest),
        "priority": priority,
        "priority_label": label(priority),
    }


def build_report_roadmap(profile, emotional_context):
    concern = safe(profile.get("concern_type"), "").lower()
    if emotional_context or "mental" in concern or "relationship" in concern:
        return [
            {"title": "Calm & Ground", "body": "Pause for a few minutes, breathe slowly, drink water, and avoid reacting while emotions are high."},
            {"title": "Talk & Clarify", "body": "Write the main worry in simple words and speak with one trusted person or supportive contact."},
            {"title": "Rebuild Routine", "body": "Protect sleep, meals, and light movement for the next few days so your mind gets steadier."},
        ]
    pain = safe(profile.get("pain"), "").lower()
    if "strong" in pain:
        return [
            {"title": "Protect & Observe", "body": "Rest the affected area, avoid strain, and note whether pain is increasing or spreading."},
            {"title": "Safe Relief", "body": "Use gentle home care only if it feels safe, stay hydrated, and avoid self-medicating."},
            {"title": "Consult If Needed", "body": "If pain stays strong, returns often, or affects daily activity, consult a qualified professional."},
        ]
    return [
        {"title": "Rest & Observe", "body": "Protect your energy, track symptoms, and avoid heavy activity today."},
        {"title": "Hydrate & Recover", "body": "Take fluids gradually, keep meals light and regular, and prioritize sleep recovery."},
        {"title": "Return Gradually", "body": "Resume routine slowly once symptoms improve; seek care if symptoms worsen or persist."},
    ]


@HealthiFy.route('/save-profile', methods=['POST'])
@login_required
def save_profile():
    data = request.get_json(silent=True) or request.form.to_dict()
    profile_data = {
        "avatar": safe(data.get("avatar"), "pulse"),
        "name": safe(data.get("name")),
        "email": safe(data.get("email"), session.get("user", "")),
        "age": safe(data.get("age")),
        "gender": safe(data.get("gender")),
        "weight": safe(data.get("weight")),
        "height_cm": safe(data.get("height_cm")),
        "height_ft": safe(data.get("height_ft")),
        "height_in": safe(data.get("height_in")),
        "bmi": safe(data.get("bmi")),
        "bmi_status": safe(data.get("bmi_status")),
        "blood_group": safe(data.get("blood_group")),
        "sugar": safe(data.get("sugar"), "no"),
        "bp": safe(data.get("bp"), "no"),
        "thyroid": safe(data.get("thyroid"), "no"),
        "heart": safe(data.get("heart"), "no"),
        "asthma": safe(data.get("asthma"), "no"),
        "allergies": safe(data.get("allergies")),
        "medicines": safe(data.get("medicines")),
        "emergency_contact": safe(data.get("emergency_contact")),
    }
    session['profile'] = profile_data
    return jsonify({"status": "ok", "profile": profile_data})


@HealthiFy.route('/account-security', methods=['GET', 'POST'])
@login_required
def account_security():
    if request.method == 'POST':
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")
        if not current_password or not new_password:
            return render_template('account_security.html', error="Please fill all password fields.")
        if new_password != confirm_password:
            return render_template('account_security.html', error="New passwords do not match.")
        if len(new_password) < 8:
            return render_template('account_security.html', error="Use at least 8 characters for a safer password.")
        return render_template('account_security.html', success="Password change request saved. If you use Supabase login, update it from Supabase Auth too.")
    return render_template('account_security.html')


@HealthiFy.route('/about')
def about():
    return render_template('about.html')


@HealthiFy.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy_policy.html')


@HealthiFy.route('/terms')
def terms():
    return render_template('terms.html')


# =========================================================
# HEALTH SCORE
# =========================================================
@HealthiFy.route('/health-score')
@login_required
def health_score_form():
    return render_template('health_score.html')


@HealthiFy.route('/calculate-score', methods=['POST'])
@login_required
def calculate_score():
    data = request.form
    try:
        age = int(safe(data.get('age'), "25"))
    except Exception:
        age = 25
    age = max(1, min(age, 122))

    sleep          = safe(data.get('sleep'), "6")
    water          = safe(data.get('water'), "2")
    activity       = safe(data.get('activity'), "low")
    symptom_detail = safe(data.get('symptom_detail'), "")

    result = calculate_health_score(
        age, sleep, water, activity,
        "yes" if symptom_detail else "none",
        symptom_detail
    )
    session['health_score']  = result
    session['symptom_text']  = symptom_detail
    return redirect('/score-result')


@HealthiFy.route('/score-result')
@login_required
def score_result():
    if 'health_score' not in session:
        return redirect('/health-score')
    return render_template('score_result.html', result=session['health_score'])


# =========================================================
# IMPROVE FLOW
# =========================================================
@HealthiFy.route('/improve')
@login_required
def improve():
    if 'health_score' not in session:
        return redirect('/health-score')
    return render_template('improve_loading.html')


@HealthiFy.route('/improve-plan')
@login_required
def improve_plan():
    if 'health_score' not in session:
        return redirect('/health-score')
    symptom_text = safe(session.get('symptom_text'), "")
    result = build_response(symptom_text)
    return render_template(
        "improve_plan.html",
        user_text=escape(symptom_text),
        cause=safe(result.get("cause")),
        effect=safe(result.get("effect")),
        solution=safe(result.get("solution"))
    )


# =========================================================
# AI CHAT
# =========================================================
@HealthiFy.route('/public-search-ai', methods=['POST'])
def public_search_ai():
    try:
        data = request.get_json(silent=True) or {}
        query = safe(data.get("query"))
        if not query:
            return jsonify({"answer": "Please ask something clearly.", "remaining": 2})

        if 'user' not in session:
            used = int(session.get('public_ai_used', 0))
            if used >= 2:
                return jsonify({
                    "answer": "Create a free Healthify account to continue your MindCare AI conversation safely.",
                    "remaining": 0,
                    "require_login": True
                })
            session['public_ai_used'] = used + 1
            remaining = max(0, 2 - session['public_ai_used'])
        else:
            remaining = None

        # Public trial should never carry old personal context or names from a previous tester/session.
        answer = ai_chat_response(query, [])
        if not answer or len(answer.strip()) < 5:
            answer = build_response(query).get("solution", "Please share a little more detail.")

        session["public_chat_history"] = [{"user": query, "ai": answer}]

        return jsonify({"answer": answer, "remaining": remaining, "require_login": False})
    except Exception:
        logging.exception("Public AI error")
        return jsonify({"answer": "Technical issue aa raha hai. Please try again.", "remaining": 0})


@HealthiFy.route('/ai')
@login_required
def ai_page():
    if request.args.get("fresh", "1") == "1":
        session['chat_history'] = []
    return render_template('ai.html')


@HealthiFy.route('/search-ai', methods=['POST'])
@login_required
def search_ai():
    try:
        data  = request.get_json(silent=True) or {}
        query = safe(data.get("query"))

        if not query:
            return jsonify({"answer": "Please ask something clearly 🙂"})

        history = session.get("chat_history", [])
        answer  = ai_chat_response(query, history)

        if not answer or len(answer.strip()) < 5:
            answer = "Thoda aur detail mein poochho, main help kar deta hoon 🙂"

        history.append({"user": query, "ai": answer})
        history = history[-3:]
        session["chat_history"] = history

        return jsonify({"answer": answer})

    except Exception:
        logging.exception("Search AI error")
        return jsonify({
            "answer": "⚠️ Thoda technical issue aa raha hai. Please dobara try karein 🙂"
        })


# =========================================================
# ANALYZE  — passes full profile to Report AI
# =========================================================
@HealthiFy.route('/analyze', methods=['POST'])
@login_required
def analyze():
    session.pop('report_data', None)

    data     = request.get_json(silent=True) or {}
    symptoms = safe(data.get('symptoms'), "General weakness")

    # Store full profile in session
    session['user_profile'] = data
    profile  = data  # use directly — already a dict

    india        = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(india).strftime("%d %B %Y, %I:%M:%S %p")

    fallback = build_response(symptoms)
    context_blob = " ".join([
        symptoms,
        safe(profile.get("concern_type")),
        safe(profile.get("stress_context")),
    ]).lower()
    emotional_context = any(word in context_blob for word in [
        "stress", "tension", "anxiety", "overthinking", "relationship", "family",
        "mental", "emotional", "lonely", "sad", "breakup"
    ])

    # ── KEY FIX: pass full profile to AI ──────────────────────
    ai_data = ai_health_response(
        user_input=symptoms,
        profile=profile        # full userdetails form data
    )

    if ai_data and isinstance(ai_data, dict):
        observed = safe(ai_data.get("observed_pattern"), fallback.get("cause"))
        severity = safe(ai_data.get("severity"),         fallback.get("effect"))
        care     = safe(ai_data.get("care_recommendation"), fallback.get("solution"))

        # Smart fallbacks — only use random if AI genuinely returned empty
        precautions  = ai_data.get("precautions")  or random_precautions()
        consultation = ai_data.get("consult_specialist") or []   # respect AI's empty
        blood_tests  = ai_data.get("suggested_tests")    or []   # respect AI's empty
        home_relief  = ai_data.get("home_relief")        or []
        thought      = safe(
            ai_data.get("thought"),
            "Small steps taken today lead to better health tomorrow."
        )

        logging.info("AI report used")

    else:
        (
            observed,
            severity,
            care,
            precautions,
            consultation,
            blood_tests,
            home_relief,
            thought,
        ) = profile_aware_report_fallback(symptoms, profile, fallback, emotional_context)
        logging.warning("Fallback report used")

    snapshot = build_report_snapshot(profile, severity, emotional_context)
    roadmap = build_report_roadmap(profile, emotional_context)

    session['report_data'] = {
        "report_id":   generate_report_id(),
        "date_time":   current_time,
        "name":        profile.get("name"),
        "age":         profile.get("age"),
        "gender":      profile.get("gender"),
        "location":    profile.get("location"),
        "weight":      profile.get("weight"),
        "height_cm":   profile.get("height_cm"),
        "concern_type": profile.get("concern_type"),
        "red_flag":    profile.get("red_flag"),
        "food_pattern": profile.get("food_pattern"),
        "sleep":       profile.get("sleep"),
        "water_intake": profile.get("water_intake"),
        "duration":    profile.get("duration"),
        "pain":        profile.get("pain"),
        "snapshot":    snapshot,
        "roadmap":     roadmap,
        "summary":     observed,
        "how_to_treat": care,
        "severe":      severity,
        "precautions": precautions,
        "consultation": consultation,
        "blood_tests": blood_tests,
        "home_relief": home_relief,
        "thought":     thought,
    }

    return jsonify({"status": "ok", "redirect": "/analyzing"})


# =========================================================
# REPORT
# =========================================================
@HealthiFy.route('/analyzing')
@login_required
def analyzing():
    if 'report_data' not in session:
        return redirect('/home')
    return render_template('analyzing.html')


@HealthiFy.route('/report')
@login_required
def report():
    if 'report_data' not in session:
        return redirect('/home')
    return render_template('report.html', report=session['report_data'])


# =========================================================
# PDF DOWNLOAD
# =========================================================
@HealthiFy.route('/download-report')
@login_required
def download_report():
    if 'report_data' not in session:
        return redirect('/home')
    report     = session['report_data']
    pdf_buffer = generate_pdf(report, STATIC_DIR)
    if not pdf_buffer:
        return redirect('/report')
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"{report['report_id']}.pdf",
        mimetype='application/pdf'
    )


# =========================================================
# RUN
# =========================================================
if __name__ == '__main__':
    HealthiFy.run(
        debug=False,
        host='0.0.0.0',
        port=5001,
        use_reloader=False
    )
