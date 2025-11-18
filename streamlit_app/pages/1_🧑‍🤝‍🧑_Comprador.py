# streamlit_app/pages/1_🧍‍♂️_Comprador.py
import streamlit as st
from pathlib import Path

# ---------------------------
# FUNCIÓN SEGURA PARA CAMBIO DE PÁGINA
# ---------------------------
def safe_switch_page(page_filename: str):
    """Evita errores si la página no existe."""
    page_path = Path(__file__).resolve().parent / page_filename
    if page_path.exists():
        st.switch_page(f"pages/{page_filename}")
    else:
        st.warning(f"No se encontró la página '{page_filename}'. Verificá el nombre del archivo o emoji.")

# ---------------------------
# CONFIGURACIÓN
# ---------------------------
st.set_page_config(page_title="Panel del Comprador", layout="centered")

# ---------------------------
# CONTROL DE ACCESO POR ROL
# ---------------------------
role = st.session_state.get("user_role", "")
if role != "COMPRADOR":
    st.warning("⚠️ No tenés permiso para acceder a este panel.")
    if st.button("Ir al panel de Vendedor"):
        safe_switch_page("2_🏪_Vendedor.py")
    st.stop()

# ---------------------------
# ESTILOS
# ---------------------------
st.markdown("""
<style>
/* Fondo general */
.stApp { background:#FF8C00; }

/* Tarjeta central */
.ecom-panel {
  max-width: 520px;
  margin: 24px auto 12px auto;
  background: #ff9b2f;
  border-radius: 14px;
  padding: 22px 22px 18px 22px;
  box-shadow: 0 8px 18px rgba(0,0,0,.25);
}

/* Chip "Cliente A" */
.badge {
  display:inline-block;
  background: #ffb768;
  color:#3a2306;
  font-weight:800;
  padding:6px 12px;
  border-radius:8px;
  margin: 2px 0 14px 4px;
}

/* Logo */
.logo {
  background:#fff;
  border-radius:16px;
  padding:16px 18px;
  margin: 0 auto 16px auto;
  width: 280px;
  text-align:center;
  box-shadow: 0 4px 12px rgba(0,0,0,.18);
  border: 2px solid #f3f3f3;
}
.logo h1 {
  margin:0;
  font-size:1.4rem;
  color:#153063;
}
.logo small { color:#666; }

/* Botones azules grandes */
.stButton > button {
  background:#0b3a83;
  color:#fff;
  border: none;
  border-radius: 8px;
  padding: 12px 16px;
  font-weight: 800;
  width: 100%;
  margin: 8px 0;
  box-shadow: 0 4px 10px rgba(0,0,0,.18);
}
.stButton > button:hover { filter: brightness(1.05); }

/* Botón SALIR (marrón) */
.btn-exit > button {
  background:#936037 !important;
}

/* Centrar el título */
h2.title { text-align:center; color:#1f2e5e; margin-top: 12px; }
</style>
""", unsafe_allow_html=True)

# ---------------------------
# UI PRINCIPAL
# ---------------------------
nombre = "Cliente A"

st.markdown('<div class="ecom-panel">', unsafe_allow_html=True)
st.markdown(f'<div class="badge">👤 {nombre}</div>', unsafe_allow_html=True)

st.markdown("""
<div class="logo">
  <h1>Ecom MKT Lab</h1>
  <small>Soluciones de Marketing Digital y Comercio Electrónico</small>
</div>
""", unsafe_allow_html=True)

col = st.container()
col.button("VER PRODUCTOS", key="b_ver_prod")
col.button("MI CARRITO", key="b_carrito")
col.button("COMENTARIOS", key="b_coment")
col.button("HISTORIAL DE COMPRAS", key="b_hist_comp")

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# BOTÓN SALIR
# ---------------------------
st.write("")
st.markdown('<div class="btn-exit">', unsafe_allow_html=True)
if st.button("SALIR", key="b_exit"):
    for k in ["user_name", "user_role", "auth_token"]:
        st.session_state.pop(k, None)
    st.success("Sesión cerrada correctamente.")
    safe_switch_page("0_🔐_Login.py")
st.markdown('</div>', unsafe_allow_html=True)


