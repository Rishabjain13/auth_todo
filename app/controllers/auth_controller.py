from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.models.user import User

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    password = password.encode("utf-8")[:72]
    return pwd.hash(password)

def verify_password(password: str, hashed: str):
    password = password.encode("utf-8")[:72]
    return pwd.verify(password, hashed)

def register_user(db: Session, name: str, email: str, password: str):
    if db.query(User).filter(User.email == email).first():
        return None

    user = User(
        name=name,
        email=email,
        password=hash_password(password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None

    if not verify_password(password, user.password):
        return None

    return user
