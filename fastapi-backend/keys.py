from fastapi import APIRouter, Depends, HTTPException, Body
from keycloak_admin import create_api_key, list_api_keys, revoke_api_key
from auth import verify_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
bearer = HTTPBearer()

def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    return verify_token(creds.credentials)

@router.get("/")
async def list_keys(user=Depends(get_current_user)):
    # if "admin" in user.get("realm_access", {}).get("roles", []):
    #     return {"keys": list_api_keys(owner_prefix="")}
    prefix = user["preferred_username"]
    keys = list_api_keys(owner_prefix=prefix)
    return {"keys": keys}

@router.post("/")
async def create_key(body: dict = Body(...), user=Depends(get_current_user)):
    name = body.get("name")
    roles = body.get("roles", [])
    if not name:
        raise HTTPException(400, "Missing 'name'")
    result = create_api_key(name=f"{user['preferred_username']}-{name}", roles=roles)
    return {"message": "API key created", **result}

@router.delete("/{key_id}")
async def revoke_key_route(key_id: str, user=Depends(get_current_user)):
    prefix = user["preferred_username"] + "-"
    if not key_id.startswith(prefix):
        raise HTTPException(403, "Not permitted")
    success = revoke_api_key(client_id=key_id)
    if not success:
        raise HTTPException(404, "Key not found")
    return {"message": "API key revoked", "client_id": key_id}
