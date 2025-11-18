# streamlit_app/pages/11_💎_Planes_Premium.py
import streamlit as st
import requests

st.set_page_config(page_title="Planes Premium", layout="centered")
st.title("💎 Planes Premium")

# ======================================
# CONFIG Y AUTH
# ======================================
try:
    BACKEND_URL = st.secrets["BACKEND_URL"]
except Exception:
    BACKEND_URL = "http://localhost:8000"

def get_headers():
    token = st.session_state.get("auth_token")
    return {"Authorization": f"Bearer {token}"} if token else {}

# ======================================
# CONSULTA DEL ESTADO PREMIUM ACTUAL
# ======================================
def fetch_current_premium():
    try:
        r = requests.get(
            f"{BACKEND_URL}/premium/status",
            headers=get_headers(),
            timeout=10
        )
        if r.status_code == 200:
            return r.json()
        return {}
    except Exception:
        return {}

premium_info = fetch_current_premium()

# ======================================
# INFORMACIÓN DEL FRONT-END
# ======================================
c1, c2 = st.columns(2)

# ========================================================
# CARD: VENDEDOR PREMIUM
# ========================================================
with c1:
    st.header("Vendedor Premium")
    st.write("""
### Beneficios:
- 🔥 +20% visibilidad en Home
- 🛍️ Publicación de **hasta 200 productos** (vs 20)
- 📊 Reportes avanzados + exportaciones
- ⚡ Soporte prioritario
    """)

    already = premium_info.get("role") == "VENDEDOR" and premium_info.get("active")

    if already:
        st.success("Ya sos **Vendedor Premium** ✨")
    else:
        if st.button("Elegir Vendedor Premium", key="premium_vendedor", type="primary"):
            payload = {"role": "VENDEDOR", "plan": "mensual"}
            try:
                r = requests.post(
                    f"{BACKEND_URL}/premium/intent",
                    json=payload,
                    headers=get_headers(),
                    timeout=10
                )
                if r.status_code == 200:
                    st.session_state["premium_intent"] = payload
                    st.success("Intento registrado ✔️ Redirigiendo…")
                    st.switch_page("pages/10_💳_Checkout.py")
                else:
                    st.error(f"Error al registrar el intento ({r.status_code})")
            except Exception:
                st.error("No se pudo conectar con el servidor.")

# ========================================================
# CARD: COMPRADOR PREMIUM
# ========================================================
with c2:
    st.header("Comprador Premium")
    st.write("""
### Beneficios:
- 🎁 Cupones exclusivos
- ⚡ Soporte prioritario
- 🔔 Alertas de precio
- 🗂️ Historial extendido y favoritos ilimitados
    """)

    already = premium_info.get("role") == "COMPRADOR" and premium_info.get("active")

    if already:
        st.success("Ya sos **Comprador Premium** ✨")
    else:
        if st.button("Elegir Comprador Premium", key="premium_comprador", type="primary"):
            payload = {"role": "COMPRADOR", "plan": "mensual"}
            try:
                r = requests.post(
                    f"{BACKEND_URL}/premium/intent",
                    json=payload,
                    headers=get_headers(),
                    timeout=10
                )
                if r.status_code == 200:
                    st.session_state["premium_intent"] = payload
                    st.success("Intento registrado ✔️ Redirigiendo…")
                    st.switch_page("pages/10_💳_Checkout.py")
                else:
                    st.error(f"Error al registrar el intento ({r.status_code})")
            except Exception:
                st.error("No se pudo conectar con el servidor.")
