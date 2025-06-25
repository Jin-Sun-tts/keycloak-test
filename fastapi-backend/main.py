from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth import verify_token
from keys import router as key_router
from roles import router as roles_router
from users import router as users_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
bearer = HTTPBearer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    try:
        return verify_token(creds.credentials)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.get("/ping")
async def ping():
    return {"pong": True}

@app.get("/protected")
def protected(user=Depends(get_current_user)):
    return {"message": "You are authenticated", "user": user}

@app.get("/admin-access")
def admin(user=Depends(lambda creds=Depends(bearer): verify_token(creds.credentials))):
    return {"message": "You have admin access", "user": user}

def require_roles(*req_roles):
    def dep(creds=Depends(bearer)):
        claims = verify_token(creds.credentials)
        roles = claims.get("realm_access", {}).get("roles", [])
        if not any(r in roles for r in req_roles):
            raise HTTPException(403, "Forbidden")
        return claims
    return dep

@app.get("/metrics/xxx")
def metrics(u=Depends(require_roles("access-metrics"))):
    return "here is the metrics"

app.include_router(key_router, prefix="/keys")
app.include_router(roles_router, prefix="/admin")
app.include_router(users_router, prefix="/admin")
