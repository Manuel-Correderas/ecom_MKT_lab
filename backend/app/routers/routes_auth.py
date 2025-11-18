from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr

from ..deps import get_db
from ..crud.user_crud import get_user_by_email
from ..security import verify_password, create_access_token  # 👈 importante

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginPayload(BaseModel):
    email: EmailStr
    password: str


@router.post("/login")
def login(payload: LoginPayload, db=Depends(get_db)):
    user = get_user_by_email(db, payload.email)

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )

    # 👇 generamos el JWT
    access_token = create_access_token({"sub": user.id})

    return {
        "ok": True,
        "user_id": user.id,
        "email": user.email,
        "roles": [ur.role.code for ur in user.roles],
        "access_token": access_token,   # 👈 CLAVE
        "token_type": "bearer",
    }
