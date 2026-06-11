from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


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

class IncidentResponse(BaseModel):
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
    unassigned: Optional[List[IncidentFormat]] = None
    available_agents: Optional[List[AgentFormat]] = None
    message: Optional[str] = None

class AssignIncidentRequest(BaseModel):
    incident_id: str
    agent_username: str