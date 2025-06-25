import sys
import json
import base64

def decode_jwt(jwt_token):
    try:
        parts = jwt_token.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid JWT format")

        payload = parts[1]
        padding = '=' * (-len(payload) % 4)
        decoded_bytes = base64.urlsafe_b64decode(payload + padding)
        decoded_json = json.loads(decoded_bytes)

        print(json.dumps(decoded_json, indent=2))
    except Exception as e:
        print(f"Error decoding JWT: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python decode_jwt.py <JWT>")
    else:
        decode_jwt(sys.argv[1])
