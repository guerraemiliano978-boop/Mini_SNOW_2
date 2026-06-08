from passlib.context import CryptContext


hash_engine = CryptContext(schemes=["bcrypt"])

def hash_password(password):
    return hash_engine.hash(password)

def verify_password(plain_password, hashed_password):
    return hash_engine.verify(plain_password, hashed_password)

