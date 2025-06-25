from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth import verify_token
from keys import router as key_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
bearer = HTTPBearer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000"],  # or ["*"] for dev
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

@app.get("/admin")
def admin(user=Depends(lambda creds=Depends(bearer): verify_token(creds.credentials, required_roles=["admin"]))):
    return {"message": "You have admin access", "user": user}

# Optional API key management routes
app.include_router(key_router, prefix="/keys")
