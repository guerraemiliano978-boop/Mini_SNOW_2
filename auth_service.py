from security import verify_password, create_token
from tables import users, engine
from sqlalchemy import select
from models import LoginReq



def get_data_by_username(request: LoginReq) -> dict | None:
        with engine.connect() as conn:
            stmt = select(users.c.username, users.c.password, users.c.role).where(users.c.username == request.username)
            return conn.execute(stmt).mappings().fetchone()


def verify_login(user: dict, request: LoginReq) -> bool: 
    if user is None:
        return False

    return verify_password(request.password, user["password"])


def parse_user_data(user: dict) -> dict: 
    data = {
        "sub": user["username"],
        "role": user["role"]
    }
    return data
    
    
def get_token(user: dict) -> str:
    user_data = parse_user_data(user)
    return create_token(user_data)



