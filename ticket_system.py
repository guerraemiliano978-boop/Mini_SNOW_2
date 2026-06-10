from sqlalchemy import select, insert
from tables import users, incidents, engine
from sqlalchemy.exc import SQLAlchemyError




def create_incident(payload: object, user: dict):
    try:
        user_id = get_id_by_username(user.get("sub"))
        with engine.begin() as conn:
            stmt = insert(incidents).values(
                short_description= payload.short_description, 
                description= payload.description,
                opened_by= user_id
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

def get_incident_list():
     with engine.connect() as conn:
        stmt = select(incidents)
        result = conn.execute(stmt)
        incident_list = []
        for row in result:
            ticket = dict(row._mapping)
            incident_list.append(ticket)

        return process_list(incident_list)
       
def process_list(incident_list):
    for ticket in incident_list:
        incident_id = ticket["id"]
        ticket["id"] = process_incident_id(incident_id)
        opened_by_id = ticket["opened_by"]
        ticket["opened_by"] = get_name_by_id(opened_by_id)
        assigned_to_id = ticket["assigned_to"]
        ticket["assigned_to"] = get_id_by_username(assigned_to_id)
    
    return incident_list

