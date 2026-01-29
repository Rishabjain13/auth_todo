# from fastapi import APIRouter, Form, Depends, HTTPException
# from fastapi.responses import FileResponse
# from sqlalchemy.orm import Session

# from app.database import SessionLocal
# from app.controllers.auth_controller import register_user, authenticate_user
# from app.core.security import create_access_token
# from app.models.user import User
# from app.deps import get_current_user

# router = APIRouter()

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# @router.get("/")
# def index_page():
#     return FileResponse("static/index.html")

# @router.get("/login")
# def login_page():
#     return FileResponse("static/login.html")

# @router.get("/register")
# def register_page():
#     return FileResponse("static/register.html")

# @router.post("/register")
# def register(
#     name: str = Form(...),
#     email: str = Form(...),
#     password: str = Form(...),
#     db: Session = Depends(get_db)
# ):
#     user = register_user(db, name, email, password)
#     if not user:
#         raise HTTPException(status_code=400)
#     return {"success": True}

# @router.post("/login")
# def login(
#     email: str = Form(...),
#     password: str = Form(...),
#     db: Session = Depends(get_db)
# ):
#     user = authenticate_user(db, email, password)
#     if not user:
#         raise HTTPException(status_code=401)

#     token = create_access_token(user.id)
#     return {"access_token": token}

# @router.post("/logout")
# def logout():
#     return {"success": True}

# @router.get("/me")
# def me(
#     user_id: int = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     user = db.query(User).filter(User.id == user_id).first()
#     if not user:
#         raise HTTPException(status_code=404)
#     return {"name": user.name, "email": user.email}

# from fastapi import APIRouter, Depends, HTTPException
# from fastapi.responses import FileResponse
# from sqlalchemy.orm import Session

# from app.database import SessionLocal
# from app.controllers.auth_controller import register_user, authenticate_user
# from app.core.security import create_access_token
# from app.models.user import User
# from app.deps import get_current_user

# router = APIRouter()

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# @router.get("/")
# def index_page():
#     return FileResponse("static/index.html")

# @router.get("/login")
# def login_page():
#     return FileResponse("static/login.html")

# @router.get("/register")
# def register_page():
#     return FileResponse("static/register.html")

# @router.post("/register")
# def register(data: dict, db: Session = Depends(get_db)):
#     user = register_user(
#         db,
#         data.get("name"),
#         data.get("email"),
#         data.get("password")
#     )
#     if not user:
#         raise HTTPException(400)
#     return {"success": True}

# @router.post("/login")
# def login(data: dict, db: Session = Depends(get_db)):
#     user = authenticate_user(
#         db,
#         data.get("email"),
#         data.get("password")
#     )
#     if not user:
#         raise HTTPException(401)

#     return {"access_token": create_access_token(user.id)}

# @router.post("/logout")
# def logout():
#     return {"success": True}

# @router.get("/me")
# def me(user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.id == user_id).first()
#     if not user:
#         raise HTTPException(404)
#     return {"name": user.name, "email": user.email}

# from fastapi import APIRouter, Depends, HTTPException
# from fastapi.responses import FileResponse
# from sqlalchemy.orm import Session

# from app.database import SessionLocal
# from app.controllers.auth_controller import register_user, authenticate_user
# from app.core.security import create_access_token
# from app.models.user import User
# from app.deps import get_current_user
# from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse

# router = APIRouter(tags=["Auth"])


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# @router.get("/")
# def index_page():
#     return FileResponse("static/index.html")


# @router.get("/login")
# def login_page():
#     return FileResponse("static/login.html")


# @router.get("/register")
# def register_page():
#     return FileResponse("static/register.html")


# @router.post("/register")
# def register(
#     data: RegisterRequest,
#     db: Session = Depends(get_db)
# ):
#     user = register_user(db, data.name, data.email, data.password)
#     if not user:
#         raise HTTPException(status_code=400, detail="User already exists")
#     return {"success": True}


# @router.post("/login", response_model=TokenResponse)
# def login(
#     data: LoginRequest,
#     db: Session = Depends(get_db)
# ):
#     user = authenticate_user(db, data.email, data.password)
#     if not user:
#         raise HTTPException(status_code=401, detail="Invalid credentials")

#     return {
#         "access_token": create_access_token(user.id),
#         "token_type": "bearer"
#     }


# @router.post("/logout")
# def logout():
#     return {"success": True}


# @router.get("/me")
# def me(
#     user_id: int = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     user = db.query(User).filter(User.id == user_id).first()
#     if not user:
#         raise HTTPException(status_code=404)
#     return {"name": user.name, "email": user.email}

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.controllers.auth_controller import register_user, authenticate_user
from app.core.security import create_access_token
from app.models.user import User
from app.deps import get_current_user
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse

router = APIRouter(tags=["Auth"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", include_in_schema=False)
def index_page():
    return FileResponse("static/index.html")


@router.get("/login", include_in_schema=False)
def login_page():
    return FileResponse("static/login.html")


@router.get("/register", include_in_schema=False)
def register_page():
    return FileResponse("static/register.html")


@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    user = register_user(db, data.name, data.email, data.password)
    if not user:
        raise HTTPException(status_code=400, detail="User already exists")
    return {"success": True}


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer"
    }


@router.post("/logout")
def logout():
    return {"success": True}


@router.get("/me")
def me(user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404)

    return {"name": user.name, "email": user.email}
