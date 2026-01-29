# from datetime import datetime, timedelta
# from jose import jwt, JWTError

# SECRET_KEY = "super-secret-key"
# ALGORITHM = "HS256"

# ACCESS_TOKEN_EXPIRE_MINUTES = 15
# REFRESH_TOKEN_EXPIRE_DAYS = 7

# def create_access_token(user_id: int):
#     payload = {
#         "sub": str(user_id),
#         "type": "access",
#         "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     }
#     return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# def create_refresh_token(user_id: int):
#     payload = {
#         "sub": str(user_id),
#         "type": "refresh",
#         "exp": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
#     }
#     return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# def decode_token(token: str):
#     try:
#         return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#     except JWTError:
#         return None
from datetime import datetime, timedelta
from jose import jwt, JWTError

SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(user_id: int):
    payload = {
        "sub": str(user_id),
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
