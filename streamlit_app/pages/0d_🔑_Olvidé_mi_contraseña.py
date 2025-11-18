# streamlit_app/pages/0d_🔑_Olvidé_mi_contraseña.py
# streamlit_app/pages/0d_🔑_Olvidé_mi_contraseña.py
import os
import requests
import streamlit as st

# hCaptcha opcional: si no está instalado, seguimos sin captcha
try:
    from streamlit_hcaptcha import st_hcaptcha
    HAS_HCAPTCHA = True
except Exception:
    HAS_HCAPTCHA = False

st.set_page_config(page_title="Olvidé mi contraseña - Ecom MKT Lab", layout="centered")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
HCAPTCHA_SITEKEY = os.getenv("HCAPTCHA_SITEKEY", "10000000-ffff-ffff-ffff-000000000001")  # testkey

PAGE_NS = "forgot_v1"
def K(s: str) -> str: return f"{PAGE_NS}:{s}"

# ---- estilos ----
st.markdown("""
<style>
.stApp { background:#FF8C00; }
.card{
  background:#fff; border-radius:18px; padding:28px;
  box-shadow:0 8px 22px rgba(0,0,0,.25);
}
.logo-box{
  background:#fff; border-radius:18px; padding:18px 22px;
  margin-bottom:18px; text-align:center;
}
.logo-title{ font-size:1.8rem; font-weight:800; color:#1f2e5e; }
.logo-sub{ font-size:.9rem; color:#666; }
</style>
""", unsafe_allow_html=True)

# Estado
st.session_state.setdefault(K("step"), 1)   # 1=start, 2=confirm
st.session_state.setdefault(K("email"), "")

# ---- llamadas backend ----
def forgot_start(email, celular, palabra, captcha_token):
    try:
        r = requests.post(
            f"{BACKEND_URL}/auth/forgot/start",
            json={"email": email, "celular": celular, "palabra": palabra, "captcha_token": captcha_token},
            timeout=15
        )
        if r.status_code == 200:
            st.session_state[K("email")] = email
            st.session_state[K("step")] = 2
            st.success("Si el email existe, te enviamos instrucciones. Ingresá el código recibido por email.")
        else:
            st.error(f"Error {r.status_code}: {r.text}")
    except Exception as e:
        st.error(f"No se pudo conectar al backend: {e}")

def forgot_finish(email, code, new_password):
    try:
        r = requests.post(
            f"{BACKEND_URL}/auth/forgot/finish",
            json={"email": email, "code": code, "new_password": new_password},
            timeout=15
        )
        if r.status_code == 200:
            st.success("Contraseña actualizada. Ahora podés iniciar sesión.")
            if st.button("Ir al Login", use_container_width=True, key=K("to_login")):
                st.switch_page("pages/0_🔐_Login.py")
        else:
            st.error(f"Error {r.status_code}: {r.text}")
    except Exception as e:
        st.error(f"No se pudo conectar al backend: {e}")

# ---- UI ----
st.write("")
col = st.columns([1,2,1])[1]
with col:
    st.markdown("""
    <div class="logo-box">
        <div class="logo-title">🛒 Ecom MKT Lab</div>
        <div class="logo-sub">Soluciones de Marketing Digital y Comercio Electrónico</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🔑 Olvidé mi contraseña")

    step = st.session_state[K("step")]

    if step == 1:
        with st.form(K("form_start"), clear_on_submit=False):
            email = st.text_input("Email registrado", key=K("email_input"))
            celular = st.text_input("Celular/Móvil (opcional)", placeholder="+54 9 11 1234-5678", key=K("cel"))
            palabra = st.text_input("Palabra de seguridad (opcional)", type="password", key=K("pal"))

            captcha_token = None
            if HAS_HCAPTCHA:
                st.caption("Completá el captcha para continuar:")
                # devuelve string o None
                captcha_token = st_hcaptcha(HCAPTCHA_SITEKEY, theme="light")

            enviar = st.form_submit_button("ENVIAR")

        if enviar:
            if not email:
                st.error("Ingresá tu email registrado.")
            elif HAS_HCAPTCHA and not captcha_token:
                st.error("Por favor, resolvé el captcha.")
            else:
                # si no hay hcaptcha, pasamos None y el backend lo ignora/valida distinto
                forgot_start(email, celular, palabra, captcha_token)

    elif step == 2:
        st.caption(f"Email: {st.session_state[K('email')]}")
        with st.form(K("form_finish"), clear_on_submit=False):
            code = st.text_input("Código recibido por email", key=K("code"))
            new_password = st.text_input("Nueva contraseña", type="password", key=K("newpwd"))
            confirmar = st.form_submit_button("CONFIRMAR")
        if confirmar:
            if not code or not new_password:
                st.error("Ingresá el código y la nueva contraseña.")
            else:
                forgot_finish(st.session_state[K("email")], code, new_password)

    st.write("")
    colA, colB = st.columns(2)
    if colA.button("Volver al Login", key=K("back_login"), use_container_width=True):
        st.switch_page("pages/0_🔐_Login.py")
    if colB.button("Cancelar", key=K("cancel"), use_container_width=True):
        st.session_state[K("step")] = 1
        st.session_state[K("email")] = ""

    st.markdown('</div>', unsafe_allow_html=True)

with st.expander("ℹ️ Ayuda y seguridad"):
    st.markdown("""
- Por seguridad, no confirmamos si un email existe o no.
- El código expira en **15 minutos**.
- Si instalás `streamlit-hcaptcha`, se activará automáticamente el captcha.
""")
