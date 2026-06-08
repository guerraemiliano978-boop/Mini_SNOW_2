from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from logic import verify_login, get_token, get_user_by_username
from security import verify_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt


app = FastAPI()
bearer = HTTPBearer()

class LoginReq(BaseModel):
    username: str
    password: str

class LoginResp(BaseModel):
    answer: str
    token: Optional[str] = None


def validate_credentials(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    token = credentials.credentials
    try:
        user = verify_token(token)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")


@app.post("/login", response_model=LoginResp)
def login(request: LoginReq):
    user = get_user_by_username(request)
    authenticated = verify_login(user, request)
    if authenticated:
        jwt = get_token(user)
        return LoginResp(
            answer= "Identity verified",
            token= jwt
        )
    else:
        return LoginResp(
            answer= "Incorrect password or username, please try again"
        )

@app.get("/main")
def get_main(current_user: dict = Depends(validate_credentials)):
    return {
        "message": f"Your token is working properly!"
    }

