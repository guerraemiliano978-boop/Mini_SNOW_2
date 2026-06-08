from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import jwt


hash_engine = CryptContext(schemes=["bcrypt"])

def hash_password(password):
    return hash_engine.hash(password)

def verify_password(plain_password, hashed_password):
    return hash_engine.verify(plain_password, hashed_password)


SECRET_KEY = "gru_will_never_figure_it_out"
ALGORITHM = "HS256"

def create_token(user_data: dict):
    data = user_data.copy()
    expiration_time = datetime.now(timezone.utc) + timedelta(minutes=15)
    data["exp"] = expiration_time
    encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token):
    result = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username = result.get("sub")
    if username is None:
        return False
    return result

