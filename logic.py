from tables import users, engine
from sqlalchemy import select
from hasher import verify_password

def verify_login(request):
    with engine.connect() as conn:
        stmt = select(users).where(users.c.username == request.username)
        result = conn.execute(stmt)
        user = result.fetchone()
        if user is None:
            return False
    
        hashed_password = user[3]
        return verify_password(request.password, hashed_password)
    
