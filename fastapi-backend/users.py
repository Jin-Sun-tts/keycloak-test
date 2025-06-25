from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from keycloak_admin import list_users, create_user, get_user_realm_roles
from auth import verify_token

router = APIRouter()
bearer = HTTPBearer()

def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    return verify_token(creds.credentials)

@router.get("/users")
def get_users(user=Depends(get_current_user)):
    users = list_users()
    return {
        "users": [
            {
                "id": u["id"],
                "username": u["username"],
                "roles": get_user_realm_roles(u["id"])
            } for u in users
        ]
    }

@router.post("/users")
def post_user(username: str, email: str, password: str, user=Depends(get_current_user)):
    user_id = create_user(username, email, password)
    return {"status": "created", "user_id": user_id}