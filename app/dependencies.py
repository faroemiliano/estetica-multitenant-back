from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.security import verify_token

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    try:

        token = credentials.credentials

        payload = verify_token(token)

        return payload

    except Exception as e:
        print(e)    
        raise HTTPException(
            status_code=401,
            detail="Token inválido"
        )