from sqlalchemy import select, insert, update
from tables import users, incidents, engine
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone




def create_incident(payload: object, user: dict):
    try:
        user_id = get_id_by_username(user.get("sub"))
        created_at = get_time()
        with engine.begin() as conn:
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
    
def process_incident_id(incident_id):
        result = f"INC{str(incident_id).zfill(4)}"
        return result

def  unprocress_incident_id(incident_id: str):
    if not incident_id.startswith("INC"):
        raise ValueError("Invalid incident ID format")
    
    return int(incident_id.replace("INC", ""))

def process_dt(dt: datetime):
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.isoformat().replace("+00:00", "Z")

def process_list(incident_list):
    for ticket in incident_list:
        incident_id = ticket["id"]
        ticket["id"] = process_incident_id(incident_id)
        opened_by_id = ticket["opened_by"]
        ticket["opened_by"] = get_name_by_id(opened_by_id)
        assigned_to_id = ticket["assigned_to"]
        ticket["assigned_to"] = get_name_by_id(assigned_to_id)
        created_at = ticket["created_at"]
        ticket["created_at"] = process_dt(created_at)
    
    return incident_list

def get_id_by_username(username):
    with engine.connect() as conn:
        stmt = select(users.c.id).where(users.c.username == username)
        result = conn.execute(stmt)
        return result.scalar_one_or_none()

def get_name_by_id(user_id):
    with engine.connect() as conn:
        stmt = select(users.c.full_name).where(users.c.id == user_id)
        result = conn.execute(stmt)
        return result.scalar_one_or_none()

def get_time():
    return datetime.now(timezone.utc)
   

def get_incident_list():
    with engine.connect() as conn:
        stmt = select(incidents)
        result = conn.execute(stmt)
        incident_list = []
        for row in result:
            ticket = dict(row._mapping)
            incident_list.append(ticket)

        return process_list(incident_list)
     
def get_incidents_opened_by_me(user):
    with engine.connect() as conn:
        user_id = get_id_by_username(user)
        stmt = select(incidents).where(incidents.c.opened_by == user_id)
        result = conn.execute(stmt)
        incident_list = []
        for row in result:
            ticket = dict(row._mapping)
            incident_list.append(ticket)

        return process_list(incident_list)
    
def get_unassigned_incidents():
    with engine.connect() as conn:
        stmt = select(incidents).where(incidents.c.assigned_to.is_(None))
        result = conn.execute(stmt)
        incident_list = []
        for row in result:
            ticket = dict(row._mapping)
            incident_list.append(ticket)

        return process_list(incident_list)
    
def get_available_agents():
    with engine.connect() as conn:
        stmt = select(users.c.username, users.c.full_name).where(users.c.role == "agent")
        result = conn.execute(stmt)
        available_agents = []
        for row in result:
            user = dict(row._mapping)
            available_agents.append(user)
        
        return available_agents

def assign_incident(inc_id, agent):
    try:
        raw_id = unprocress_incident_id(inc_id)
        with engine.begin() as conn:
            stmt = update(incidents).where(incidents.c.id == raw_id).values(assigned_to= agent)
            conn.execute(stmt)
            return True
    except Exception as e:
        print(f"Database error: {e}")


assign_incident("INC0001", "rockstar123")
    
print(get_incident_list())
print(get_unassigned_incidents())