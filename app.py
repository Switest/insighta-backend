from urllib import response

import jwt
import os
import requests
import logging
from flask import Flask, request, jsonify, make_response
from functools import wraps
from datetime import datetime, timedelta, timezone
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Setup logging for Stage 3 requirements
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# --- CONFIGURATION ---
# Your GitHub Credentials
GITHUB_CLIENT_ID = "Ov23lioOuo3pSVfCqH0y"
GITHUB_CLIENT_SECRET = "c143b6b759689b0a9599652d0a8957d1697b615f"
SECRET_KEY = "a_very_long_and_extremely_secret_key_12345"

# --- MIDDLEWARE ---
CORS(app, supports_credentials=True, origins=[
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:5500", 
    "http://localhost:5500"
])

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# --- AUTH HELPERS ---

def generate_tokens(user_data):
    """Creates Access Token (15m) and Refresh Token (7d)"""
    now = datetime.now(timezone.utc)
    
    access_payload = {
        "user_id": user_data.get("id"),
        "role": user_data.get("role", "analyst"),
        "exp": now + timedelta(minutes=15),
        "iat": now
    }
    
    refresh_payload = {
        "user_id": user_data.get("id"),
        "exp": now + timedelta(days=7),
        "iat": now
    }
    
    access_token = jwt.encode(access_payload, SECRET_KEY, algorithm="HS256")
    refresh_token = jwt.encode(refresh_payload, SECRET_KEY, algorithm="HS256")
    return access_token, refresh_token

def require_auth(role=None):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Stage 3: Checks Cookie (Web) or Authorization Header (CLI)
            # DEBUG: See what cookies arrived
            print(f"DEBUG: All Cookies received: {request.cookies}")

            token = request.cookies.get("access_token") or \
                    request.headers.get("Authorization", "").replace("Bearer ", "")

            if not token:
                print("DEBUG: No token found in cookies or headers!")
                return jsonify({"error": "Authentication required"}), 401

            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                # RBAC (Role-Based Access Control)
                if role and payload.get("role") != role and payload.get("role") != "admin":
                    return jsonify({"error": "Forbidden: Insufficient permissions"}), 403

                request.user = payload
                logger.info(f"Authorized access: User {payload['user_id']} to {request.path}")

            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token expired"}), 401
            except Exception as e:
                logger.info(f"Authentication failed: {e}")
                return jsonify({"error": "Invalid token"}), 401

            return f(*args, **kwargs)
        return decorated
    return decorator

# --- ROUTES ---

@app.route('/api/v1/auth/callback', methods=['GET'])
def github_callback():
    code = request.args.get('code')
    if not code:
        return jsonify({"error": "No code provided from GitHub"}), 400

    # 1. Exchange Code for GitHub Token
    token_res = requests.post(
        'https://github.com/login/oauth/access_token',
        data={
            'client_id': GITHUB_CLIENT_ID,
            'client_secret': GITHUB_CLIENT_SECRET,
            'code': code
        },
        headers={'Accept': 'application/json'}
    ).json()

    if "error" in token_res:
        return jsonify(token_res), 400

    # 2. Get GitHub User Info
    user_res = requests.get(
        'https://api.github.com/user',
        headers={'Authorization': f"Bearer {token_res.get('access_token')}"}
    ).json()

    # 3. Create Session Tokens (Defaulting to Admin for your setup)
    user_info = {"id": user_res.get('id'), "role": "admin"}
    access_token, refresh_token = generate_tokens(user_info)

    # 4. Prepare UI for CLI and Cookie for Web
    html_content = f"""
    <html>
        <body style="font-family: sans-serif; text-align: center; padding: 50px;">
            <h1 style="color: #2ea44f;">Insighta Labs+ Login Successful</h1>
            <p>Paste these into your CLI to complete login:</p>
            <div style="background: #f6f8fa; padding: 20px; border-radius: 6px; display: inline-block; text-align: left; max-width: 80%;">
                <strong>Access Token:</strong> <code style="word-break: break-all; color: #005cc5;">{access_token}</code><br><br>
                <strong>Refresh Token:</strong> <code style="word-break: break-all; color: #d73a49;">{refresh_token}</code>
            </div>
            <p><a href="http://localhost:8000">Return to Web Portal</a></p>
        </body>
    </html>
    """
    response = make_response(html_content)
    
    # 5. Secure HTTP-Only Cookie
    # This is the "Universal" local setting
    response.set_cookie(
        "access_token",
        access_token,
        httponly=True,
        samesite='Lax',   # Standard setting for same-origin/top-level navigation
        secure=False,     # MUST be False for http://127.0.0.1
        path='/',         # Makes it available to /api/v1/profiles
        max_age=3600      # Expires in 1 hour
    )
    
    # IMPORTANT: Ensure you are returning the 'response' object, not just the jsonify
    return response

@app.route('/api/v1/profiles', methods=['GET'])
@require_auth(role="analyst")
def get_profiles():
    # Pagination Requirement
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    
    profiles = [{"id": 1, "name": "Insighta User", "role": "analyst"}]
    
    return jsonify({
        "status": "success",
        "data": profiles,
        "metadata": {
            "page": page,
            "limit": limit,
            "total": len(profiles)
        }
    })

@app.route('/api/v1/profiles/export', methods=['GET'])
@require_auth(role="admin")
def export_profiles():
    import pandas as pd
    from io import StringIO
    
    data = [{"id": 1, "name": "Insighta User", "role": "analyst"}]
    df = pd.DataFrame(data)
    
    output = StringIO()
    df.to_csv(output, index=False)
    
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=profiles_export.csv"
    response.headers["Content-type"] = "text/csv"
    return response

if __name__ == "__main__":
    app.run(port=5000, debug=True)
# Note: In production, set debug=False and ensure SECRET_KEY is secure and not hardcoded.