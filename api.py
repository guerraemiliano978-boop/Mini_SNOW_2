from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from auth_service import verify_login, get_token, get_user_by_username
from security import verify_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from ticket_system import create_incident, get_incident_list


app = FastAPI()
bearer = HTTPBearer()

class LoginReq(BaseModel):
    username: str
    password: str

class LoginResp(BaseModel):
    answer: str
    token: Optional[str] = None

class CreateIncidentRequest(BaseModel):
    short_description: str
    description: str

class CreateIncidentResponse(BaseModel):
    status: str
    ticket_id: Optional[str] = None
    message: Optional[str] = None

class IncidentTicketFormat(BaseModel):
    id: str
    short_description: str
    description: str
    opened_by: str
    assigned_to: Optional[str]
    status: str
    resolution_notes: Optional[str]

class IncidentListResponse(BaseModel):
    tickets: List[IncidentTicketFormat]



def validate_credentials_and_role(required_role):
    def dependency(current_user: dict = Depends(validate_credentials)):
        if current_user["role"] != required_role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have enough permissions")
    
        return current_user
    return dependency


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

@app.post("/incident/create", response_model=CreateIncidentResponse)
def request_incident_creation(payload: CreateIncidentRequest, current_user: dict = Depends(validate_credentials)):
    ticket_id = create_incident(payload, current_user)
    if ticket_id:
        return CreateIncidentResponse(
            status= "Success",
            ticket_id= ticket_id
        )
    else:
        return CreateIncidentResponse(
            status= "failure",
            message= "Something, went wrong, please try again later"
        )

@app.get("/incident/get/tables", response_model=IncidentListResponse)
def request_incidents_list(current_user: dict = Depends(validate_credentials_and_role("agent"))):
    incidents_list = get_incident_list()
    return IncidentListResponse(
        tickets= incidents_list
    )
