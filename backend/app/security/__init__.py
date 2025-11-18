# backend/app/security/__init__.py
from passlib.context import CryptContext
from fastapi import HTTPException, status

from .tokens import create_access_token, SECRET_KEY, ALGORITHM  # 👈 reexportamos
# OJO: NO volvemos a importar tokens acá para evitar bucles raros

# Usamos pbkdf2_sha256 como scheme para las contraseñas
pwd_ctx = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(p: str) -> str:
    """Hashea una contraseña en texto plano."""
    return pwd_ctx.hash(p)


def verify_password(p: str, h: str) -> bool:
    """Verifica una contraseña vs el hash almacenado."""
    return pwd_ctx.verify(p, h)


def require_vendor(user):
    """
    Verifica que el usuario tenga el rol VENDEDOR.
    Usa user.roles y cada elemento debe tener .role.code
    """
    codes = {
        ur.role.code
        for ur in getattr(user, "roles", [])
        if getattr(ur, "role", None)
    }

    if "VENDEDOR" not in codes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol VENDEDOR.",
        )
