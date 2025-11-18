# tests/test_auth_login.py

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db import SessionLocal
from backend.app.models.models import User
from backend.app.security import hash_password

client = TestClient(app)


def crear_usuario_de_prueba():
    """
    Crea un usuario directamente en la base de datos para probar el login.
    """
    db = SessionLocal()
    try:
        # Limpiar si ya existe
        existing = db.query(User).filter_by(email="login_test@mktlab.com").first()
        if existing:
            db.delete(existing)
            db.commit()

        u = User(
            nombre="Login",
            apellido="Test",
            tipo_doc="DNI",
            nro_doc="99999999",
            email="login_test@mktlab.com",
            tel="12345678",
            palabra_seg="gato",
            password_hash=hash_password("Test123!"),
            acepta_terminos=True,
        )
        db.add(u)
        db.commit()
        db.refresh(u)
        return u
    finally:
        db.close()


def test_login_exitoso():
    """
    Verifica que el login con credenciales correctas funcione.
    """
    crear_usuario_de_prueba()

    payload = {
        "email": "login_test@mktlab.com",
        "password": "Test123!",
    }
    resp = client.post("/auth/login", json=payload)

    # 1) Debe responder OK
    assert resp.status_code == 200, f"Status: {resp.status_code}, body: {resp.text}"

    data = resp.json()

    # 2) Debe marcar ok = True
    assert data.get("ok") is True

    # 3) Debe devolver el mismo email
    assert data.get("email") == payload["email"]

    # 4) Debe haber un user_id
    assert "user_id" in data and isinstance(data["user_id"], str)

    # 5) roles debe existir y ser lista
    assert "roles" in data
    assert isinstance(data["roles"], list)


def test_login_password_incorrecta():
    """
    Verifica que con password incorrecta el login falle.
    """
    crear_usuario_de_prueba()

    payload = {
        "email": "login_test@mktlab.com",
        "password": "MalaClave!",
    }
    resp = client.post("/auth/login", json=payload)

    # 401 es lo típico para credenciales inválidas
    assert resp.status_code in (400, 401), f"Status: {resp.status_code}, body: {resp.text}"
