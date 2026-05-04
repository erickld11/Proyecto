from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.models import User
from app.schemas import UserRegister, UserLogin, UserOut, Token
from app.services import hash_password, verify_password, create_access_token, get_current_user
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])


@router.post("/register", response_model=UserOut, status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    """Registra un nuevo usuario con contraseña cifrada con bcrypt."""
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    # El primer usuario registrado es automáticamente administrador
    is_first_user = db.query(User).count() == 0

    user = User(
        name=data.name,
        email=data.email,
        hashed_password=hash_password(data.password),
        company=data.company,
        is_admin=is_first_user,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    """Login con JWT. El sub del token es el id como string."""
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas")

    token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    return {"access_token": token, "token_type": "bearer", "user": user}


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """Devuelve el perfil del usuario autenticado."""
    return current_user
