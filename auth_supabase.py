from supabase_client import require_supabase


# SEND OTP
def send_otp(email):
    return require_supabase().auth.sign_in_with_otp({
        "email": email,
        "options": {"should_create_user": True}
    })


# VERIFY OTP
def verify_otp(email, token):
    return require_supabase().auth.verify_otp({
        "email": email,
        "token": token,
        "type": "email"
    })


# GOOGLE LOGIN
def google_login(redirect_to):
    return require_supabase().auth.sign_in_with_oauth({
        "provider": "google",
        "options": {
            "redirect_to": redirect_to
        }
    })
