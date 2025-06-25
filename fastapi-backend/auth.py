import os
import time
import requests
from jose import jwt, JWTError
from dotenv import load_dotenv

load_dotenv()

KEYCLOAK_URL = os.getenv("KEYCLOAK_SERVER")
REALM = os.getenv("KEYCLOAK_REALM", "demo")
ALGO = "RS256"
AUDIENCE = os.getenv("KEYCLOAK_CLIENT_ID", "api-backend")

def fetch_jwks(retries=10, delay=3):
    jwks_url = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/certs"
    print(f"Fetching JWKS from: {jwks_url}")
    for i in range(retries):
        try:
            print(f"Attempt {i + 1} to fetch JWKS...")
            resp = requests.get(jwks_url)
            if resp.status_code == 200:
                print("JWKS fetched successfully.")
                return resp.json()
            else:
                print(f"Failed with status: {resp.status_code}")
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error: {e}")
        time.sleep(delay)
    raise RuntimeError("Failed to retrieve JWKS from Keycloak.")


JWKS = fetch_jwks()

def verify_token(token: str, audience: str = AUDIENCE, required_roles=None):
    try:
        unverified = jwt.get_unverified_claims(token)
        print("Token issuer:", unverified.get("iss"))
        claims = jwt.decode(
            token,
            JWKS,
            algorithms=[ALGO],
            audience=audience,
            issuer=f"{KEYCLOAK_URL}/realms/{REALM}"
        )
    except JWTError as e:
        raise ValueError(f"Invalid token: {e}")

    if required_roles:
        roles = claims.get("realm_access", {}).get("roles", [])
        if not any(role in roles for role in required_roles):
            raise PermissionError("User does not have required role(s).")

    return claims
