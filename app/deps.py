from fastapi import Header, HTTPException
from app.core.security import decode_token

def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401)

    scheme, token = authorization.split()
    if scheme != "Bearer":
        raise HTTPException(status_code=401)

    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401)

    return int(payload["sub"])
