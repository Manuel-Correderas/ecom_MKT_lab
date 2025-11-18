# streamlit_app/auth_helpers.py
import os
import streamlit as st
from dotenv import load_dotenv 

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

def get_backend_url() -> str:
    return BACKEND_URL

def set_auth_session(data: dict):
    """
    Guarda en session_state todo lo que venga del login.
    Espera al menos: access_token, user_id, email, roles.
    """
    st.session_state["auth_token"] = data.get("access_token")
    st.session_state["auth_user_id"] = data.get("user_id")
    st.session_state["auth_email"] = data.get("email")
    st.session_state["auth_roles"] = data.get("roles", [])
    st.session_state["is_authenticated"] = bool(data.get("access_token"))

def auth_headers() -> dict:
    tok = st.session_state.get("auth_token")
    return {"Authorization": f"Bearer {tok}"} if tok else {}

def require_login() -> bool:
    """Devuelve True si hay token, si no muestra aviso y devuelve False."""
    if "auth_token" not in st.session_state or not st.session_state["auth_token"]:
        st.warning("Tenés que iniciar sesión para continuar.")
        st.page_link("pages/0_🔐_Login.py", label="Ir al Login", icon="🔐")
        return False
    return True
