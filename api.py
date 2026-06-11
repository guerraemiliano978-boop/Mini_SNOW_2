from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from auth_service import verify_login, get_token, get_user_by_username
from security import verify_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from ticket_system import create_incident, get_incident_list, get_incidents_opened_by_me, get_available_agents, get_unassigned_incidents
from datetime import datetime


#INSTANCES
app = FastAPI()
bearer = HTTPBearer()


#VALIDATION MODELS
class LoginReq(BaseModel):
    username: str
    password: str

class LoginResp(BaseModel):
    answer: str
    token: Optional[str] = None

class CreateIncidentRequest(BaseModel):
    short_description: str
    description: str
    priority: int

class CreateIncidentResponse(BaseModel):
    status: str
    ticket_id: Optional[str] = None
    message: Optional[str] = None

class IncidentFormat(BaseModel):
    id: str
    short_description: str
    description: str
    opened_by: str
    created_at: str
    assigned_to: Optional[str]
    priority: int
    status: str
    resolution_notes: Optional[str]
    resolved_at: Optional[datetime]

class AgentFormat(BaseModel):
    username: str
    full_name: str

class IncidentListResponse(BaseModel):
    tickets: List[IncidentFormat]

class IncidentUnassignedResponse(BaseModel):
    unassigned: List[IncidentFormat]
    available_agents: List[AgentFormat]



#VALIDATION AND ROLE ACCESS FUNCTIONS
def validate_credentials_and_role(required_roles):
    if isinstance(required_roles, str):
        required_roles = (required_roles,)

    def dependency(current_user: dict = Depends(validate_credentials)):
        if current_user["role"] not in required_roles:
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


#ROUTES
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

@app.get("/incident/get/all", response_model=IncidentListResponse)
def request_incidents_list( _: dict = Depends(validate_credentials_and_role("admin"))):
    incidents_list = get_incident_list()
    return IncidentListResponse(
        tickets= incidents_list
    )

@app.get("/incidents/get/unassigned-with-agents", response_model=IncidentUnassignedResponse)
def unassigned_incidents_with_agents( _: dict = Depends(validate_credentials_and_role("admin"))):
    incidents_list = get_unassigned_incidents()
    available_agents = get_available_agents()
    return IncidentUnassignedResponse(
        unassigned= incidents_list,
        available_agents= available_agents
    )




@app.get("/incident/get/opened_by/me", response_model=IncidentListResponse)
def incidents_opened_by_me(current_user: dict = Depends(validate_credentials)):
    user = current_user["sub"]
    incidents_list = get_incidents_opened_by_me(user)
    return IncidentListResponse(
            tickets= incidents_list
        )
    
        
