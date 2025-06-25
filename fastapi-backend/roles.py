from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from keycloak_admin import create_realm_role, list_realm_roles, assign_role_to_user
from auth import verify_token

router = APIRouter()
bearer = HTTPBearer()

def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    return verify_token(creds.credentials)

@router.get("/roles")
def get_roles(user=Depends(get_current_user)):
    return {"roles": [r['name'] for r in list_realm_roles()]}

@router.post("/roles")
def post_role(name: str, user=Depends(get_current_user)):
    create_realm_role(name)
    return {"status": "created", "role": name}

@router.post("/roles/assign")
def post_assign(user_id: str, role_name: str, user=Depends(get_current_user)):
    assign_role_to_user(user_id, role_name)
    return {"status": "assigned", "user_id": user_id, "role": role_name}
