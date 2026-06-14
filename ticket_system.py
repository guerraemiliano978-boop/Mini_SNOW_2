from models import CreateIncidentRequest, AssignIncidentRequest, ResolveIncidentRequest
from sqlalchemy import select, insert, update
from tables import users, incidents, engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine import Connection
from datetime import datetime, timezone
from sqlalchemy.sql import Select




def create_incident(payload: CreateIncidentRequest, user: dict) -> str|bool:
    try: 
        created_at = get_time()
        with engine.begin() as conn:
            user_id = get_id_by_username(user.get("sub"), conn)
            stmt = insert(incidents).values(
                short_description= payload.short_description, 
                description= payload.description,
                opened_by= user_id,
                created_at= created_at,
                priority= payload.priority
                )
            result = conn.execute(stmt)
        incident_id = result.inserted_primary_key[0]
        processed_id = process_incident_id(incident_id)
        return processed_id
    except SQLAlchemyError as e:
         print(f"Database error: {e}")
         return False


def fetch_incident_list(stmt: Select, conn: Connection):
    result = conn.execute(stmt)
    incident_list = []
    for row in result:
        ticket = dict(row._mapping)
        incident_list.append(ticket)

    return process_list(incident_list, conn)
    

def process_incident_id(incident_id: int) -> str:
        result = f"INC{str(incident_id).zfill(4)}"
        return result


def  unprocress_incident_id(incident_id: str) -> int:
    if not incident_id.startswith("INC"):
        raise ValueError("Invalid incident ID format")
    
    return int(incident_id.replace("INC", ""))


def process_dt(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.isoformat().replace("+00:00", "Z")


def process_list(incident_list: list, conn: Connection) -> list:
    for ticket in incident_list:
        incident_id = ticket["id"]
        ticket["id"] = process_incident_id(incident_id)
        opened_by_id = ticket["opened_by"]
        print(opened_by_id)
        ticket["opened_by"] = get_name_by_id(opened_by_id, conn)
        assigned_to_id = ticket["assigned_to"]
        print(assigned_to_id)
        ticket["assigned_to"] = get_name_by_id(assigned_to_id, conn)
        created_at = ticket["created_at"]
        ticket["created_at"] = process_dt(created_at)
    
    return incident_list
    

def get_id_by_username(username: str, conn: Connection) -> int:
    stmt = select(users.c.id).where(users.c.username == username)
    result = conn.execute(stmt)
    return result.scalar_one_or_none()


def get_name_by_id(user_id: int, conn: Connection) -> str:
        stmt = select(users.c.full_name).where(users.c.id == user_id)
        result = conn.execute(stmt)
        return result.scalar_one_or_none() 


def get_time() -> datetime:
    return datetime.now(timezone.utc)
   

def get_incident_list() -> list:
    with engine.connect() as conn:
        stmt = select(incidents)
        return fetch_incident_list(stmt, conn)
    
     
def get_incidents_opened_by_me(username: str) -> list:
    with engine.connect() as conn:
        user_id = get_id_by_username(username, conn)
        stmt = select(incidents).where(incidents.c.opened_by == user_id)
        return fetch_incident_list(stmt, conn)
    
    
def get_incidents_assigned_to_me(username: str) -> list:
    with engine.connect() as conn:
        user_id = get_id_by_username(username, conn)
        stmt = select(incidents).where(incidents.c.assigned_to == user_id)
        return fetch_incident_list(stmt, conn)
    
    
def get_unassigned_incidents() -> list:
    with engine.connect() as conn:
        stmt = select(incidents).where(incidents.c.assigned_to.is_(None))
        return fetch_incident_list(stmt, conn)
    
    
def get_available_agents() -> list:
    with engine.connect() as conn:
        stmt = select(users.c.username, users.c.full_name).where(users.c.role == "agent")
        result = conn.execute(stmt)
        available_agents = []
        for row in result:
            user = dict(row._mapping)
            available_agents.append(user)
        
        return available_agents
    

def assign_incident(payload: AssignIncidentRequest) -> bool:
    try:
        raw_id = unprocress_incident_id(payload.incident_id)
        with engine.begin() as conn:
            agent_id = get_id_by_username(payload.agent_username, conn)
            stmt = update(incidents).where(incidents.c.id == raw_id).values(assigned_to= agent_id, status= "in progress")
            conn.execute(stmt)
            return True
    except SQLAlchemyError as e:
        print(f"Database error: {e}")


def resolve_incident(payload: ResolveIncidentRequest, user: dict) -> bool:
    try:
        raw_id = unprocress_incident_id(payload.incident_id)
        with engine.begin() as conn:
            user_id = get_id_by_username(user["sub"], conn)
            stmt = select(incidents).where(incidents.c.id == raw_id, incidents.c.assigned_to == user_id)
            result = conn.execute(stmt)
            if result.fetchall() or user["role"] == "admin":
                current_time = get_time()
                stmt = update(incidents).where(incidents.c.id == raw_id).values(
                    status= "resolved",
                    resolution_notes= payload.resolution_notes,
                    resolved_at= current_time)
                conn.execute(stmt)
                return True

            else:
                return False
            
    except SQLAlchemyError as e:
        print(f"Database error: {e}")



