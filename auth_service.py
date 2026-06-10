from tables import users, engine
from sqlalchemy import select
from security import verify_password, create_token


def get_user_by_username(request: object):
    with engine.connect() as conn:
        stmt = select(users).where(users.c.username == request.username)
        result = conn.execute(stmt)
        return result.fetchone()

def verify_login(user: tuple, request: object):
    if user is None:
        return False

    hashed_password = user[3]
    return verify_password(request.password, hashed_password)

def get_user_data(user: tuple): 
    data = {
        "sub": user[2],
        "role": user[4]
    }
    return data
    
def get_token(user: tuple):
    user_data = get_user_data(user)
    return create_token(user_data)



