from ticket_system import create_incident, get_incident_list, get_incidents_opened_by_me, get_incidents_assigned_to_me, get_available_agents, get_unassigned_incidents, assign_incident
from models import LoginReq, LoginResp, IncidentResponse, CreateIncidentRequest, IncidentListResponse, IncidentUnassignedResponse, AssignIncidentRequest
from dependencies import validate_credentials, validate_credentials_and_role
from auth_service import verify_login, get_token, get_user_by_username
from fastapi import FastAPI, Depends



app = FastAPI()



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

@app.post("/incident/create", response_model=IncidentResponse)
def request_incident_creation(payload: CreateIncidentRequest, current_user: dict = Depends(validate_credentials)):
    ticket_id = create_incident(payload, current_user)
    if ticket_id:
        return IncidentResponse(
            status= "Success",
            ticket_id= ticket_id
        )
    else:
        return IncidentResponse(
            status= "failure",
            message= "Something, went wrong, please try again later"
        )

@app.get("/incident/get/all", response_model=IncidentListResponse)
def request_incidents_list( _: dict = Depends(validate_credentials_and_role("admin"))):
    incidents_list = get_incident_list()
    return IncidentListResponse(
        tickets= incidents_list
    )

@app.get("/incident/get/unassigned-with-agents", response_model=IncidentUnassignedResponse)
def unassigned_incidents_with_agents( _: dict = Depends(validate_credentials_and_role("admin"))):
    incidents_list = get_unassigned_incidents()
    available_agents = get_available_agents()
    if not incidents_list:
        return IncidentUnassignedResponse(
            message= "There are no unsassigned tickets at the moment"
        )
    
    else:
        return IncidentUnassignedResponse(
            unassigned= incidents_list,
            available_agents= available_agents
        )

@app.post("/incident/assign", response_model=IncidentResponse)
def assign_incident_request(payload: AssignIncidentRequest, _: dict = Depends(validate_credentials_and_role("admin"))):
    is_valid = assign_incident(payload)
    if is_valid:
        return IncidentResponse(
            status= "success"
        )
    else:
        return IncidentResponse(
            status= "failure",
            message= "something went wrong, please try again in a moment"
        )

@app.get("/incident/get/opened_by/me", response_model=IncidentListResponse)
def incidents_opened_by_me(current_user: dict = Depends(validate_credentials)):
    username = current_user["sub"]
    incidents_list = get_incidents_opened_by_me(username)
    return IncidentListResponse(
            tickets= incidents_list
        )

@app.get("/incident/get/assigned_to/me", response_model=IncidentListResponse)
def incidents_assigned_to_me(current_user: dict = Depends(validate_credentials)):
    username = current_user["sub"]
    incidents_list = get_incidents_assigned_to_me(username)
    return IncidentListResponse(
        tickets= incidents_list
    )
        
