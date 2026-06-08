from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from logic import verify_login


app = FastAPI()

class LoginReq(BaseModel):
    username: str
    password: str

class LoginResp(BaseModel):
    answer: str
    token: Optional[str] = None



@app.post("/login", response_model=LoginResp)
def login(request: LoginReq):
    authenticated = verify_login(request)
    if authenticated:
        return LoginResp(
            answer= "Identity verified",
            token= "here is your token"
        )
    else:
        return LoginResp(
            answer= "Incorrect password or username, please try again"
        )


