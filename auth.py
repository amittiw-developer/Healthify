from werkzeug.security import generate_password_hash, check_password_hash
from supabase_client import require_supabase


# =========================
# SIGNUP FUNCTION
# =========================
def create_user(name, email, password):

    hashed_password = generate_password_hash(password)

    data = {
        "name": name,
        "email": email,
        "password": hashed_password
    }

    response = require_supabase().table("users").insert(data).execute()

    return response


# =========================
# LOGIN FUNCTION
# =========================
def login_user(email, password):

    response = require_supabase().table("users").select("*").eq("email", email).execute()

    if not response.data:
        return None

    user = response.data[0]

    if check_password_hash(user["password"], password):
        return user

    return None
