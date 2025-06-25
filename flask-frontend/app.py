import os
from flask import Flask, redirect, url_for, session, render_template
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, template_folder="templates")
app.secret_key = os.getenv("FLASK_SECRET", "super-secret")

# Keycloak config from environment
KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://localhost:8080")
REALM = os.getenv("KEYCLOAK_REALM", "demo")
CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID")
CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET")

# Full metadata URL
metadata_url = f"{KEYCLOAK_URL}/realms/{REALM}/.well-known/openid-configuration"

# Configure OAuth
oauth = OAuth(app)
oauth.register(
    name="keycloak",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    server_metadata_url=metadata_url,
    client_kwargs={"scope": "openid profile"},
)

# Routes
@app.route("/")
def index():
    user = session.get("user")
    return render_template("index.html", user=user)

@app.route("/login")
def login():
    redirect_uri = url_for("auth_callback", _external=True)
    return oauth.keycloak.authorize_redirect(redirect_uri)

@app.route("/auth/callback")
def auth_callback():
    token = oauth.keycloak.authorize_access_token()
    id_token = token.get("id_token")
    access_token = token.get("access_token")
    # Save the ID token and access token in session
    session["user"] = token.get("userinfo") or {}  # Optional: request userinfo endpoint
    session["access_token"] = access_token
    session["id_token"] = id_token
    print(access_token)
    return redirect("/")

@app.route("/logout")
def logout():
    id_token = session["id_token"]
    session.clear()

    logout_url = (
        f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/logout"
        f"?post_logout_redirect_uri={url_for('index', _external=True)}"
        f"&id_token_hint={id_token}"
    )
    return redirect(logout_url)


if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
