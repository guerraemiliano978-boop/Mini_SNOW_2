from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, status, HTTPException
from security import verify_token
import jwt


bearer = HTTPBearer()




def validate_credentials_and_role(required_roles):
    if isinstance(required_roles, str):
        required_roles = (required_roles,)

    def dependency(current_user: dict = Depends(validate_credentials)):
        if current_user["role"] not in required_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have enough permissions")
    
        return current_user
    return dependency


def validate_credentials(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    token = credentials.credentials
    try:
        user = verify_token(token)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

