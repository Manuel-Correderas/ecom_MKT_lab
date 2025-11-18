import os
import requests
import streamlit as st

st.set_page_config(page_title="Alta / Edición de Usuario", layout="centered")

# ------------------- Config -------------------
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
if "last_user_id" not in st.session_state:
    st.session_state["last_user_id"] = None

# Namespace para evitar claves duplicadas
PAGE_NS = "alta_usuario_v2"
def K(s: str) -> str:
    return f"{PAGE_NS}:{s}"

# ------------------- Estilos -------------------
st.markdown("""
<style>
.stApp { background:#FF8C00; }
.panel{
  background: #f79b2f;
  border-radius: 12px;
  padding: 18px;
  box-shadow: 0 8px 18px rgba(0,0,0,.18);
}
.hdr{ font-size:1.25rem; font-weight:800; color:#1f2e5e; margin-bottom:8px; }
.lbl{ font-weight:700; color:#1f2e5e; }
.small{ color:#333; font-size:.9rem; }
.btn-azul{
  background:#0b3a91; color:#fff; border:none; border-radius:8px;
  padding:.65rem 1rem; font-weight:800; width:100%;
}
.btn-marron{
  background:#936037; color:#fff; border:none; border-radius:8px;
  padding:.65rem 1rem; font-weight:800; width:100%;
}
.divisor{ border-top:2px solid rgba(0,0,0,.1); margin:12px 0; }
</style>
""", unsafe_allow_html=True)

# ------------------- Helpers backend -------------------
def _build_payload(
    nombre, apellido, tipo_doc, nro_doc, email, tel,
    palabra_seg, password, acepto,
    dom_env, dom_ent, alias_cbu, wallet, red,
    comprador_ck, vendedor_ck
):
    # ADMIN nunca se envía desde la UI
    roles = []
    if comprador_ck: roles.append("COMPRADOR")
    if vendedor_ck: roles.append("VENDEDOR")
    if not roles: roles = ["COMPRADOR"]

    domicilio_envio = None
    if dom_env.strip():
        domicilio_envio = {
            "tipo": "ENVIO",
            "calle_y_numero": dom_env.strip(),
            "ciudad": "",
            "provincia": "",
            "pais": "",
            "cp": ""
        }

    domicilio_entrega = None
    if dom_ent.strip():
        domicilio_entrega = {
            "tipo": "ENTREGA",
            "calle_y_numero": dom_ent.strip(),
            "ciudad": "",
            "provincia": "",
            "pais": "",
            "cp": ""
        }

    banking = {"cbu_o_alias": alias_cbu.strip()} if alias_cbu.strip() else None
    wallets = [{"red": red, "address": wallet.strip()}] if wallet.strip() else None

    payload = {
        "nombre": nombre.strip(),
        "apellido": apellido.strip(),
        "tipo_doc": tipo_doc,
        "nro_doc": nro_doc.strip(),
        "email": email.strip(),
        "tel": tel.strip() if tel else None,
        "palabra_seg": palabra_seg.strip() if palabra_seg else None,
        "password": password,
        "acepta_terminos": bool(acepto),
        "domicilio_envio": domicilio_envio,
        "domicilio_entrega": domicilio_entrega,
        "banking": banking,
        "wallets": wallets,
        "roles": roles
    }
    return payload

def _post_user(payload):
    return requests.post(f"{BACKEND_URL}/users", json=payload, timeout=20)

def _put_user(user_id, payload):
    return requests.put(f"{BACKEND_URL}/users/{user_id}", json=payload, timeout=20)

def _upload_kyc(user_id, kyc_files):
    files = []
    for f in kyc_files:
        mime = getattr(f, "type", None) or "application/octet-stream"
        files.append(("files", (f.name, f.getvalue(), mime)))
    return requests.post(f"{BACKEND_URL}/users/{user_id}/kyc", files=files, timeout=60)

def _limpieza_rapida():
    for key in list(st.session_state.keys()):
        if key.startswith(PAGE_NS + ":") or key.startswith("form_"):
            st.session_state.pop(key, None)

# ------------------- Defaults de roles (desde pantalla 0b) -------------------
pref = st.session_state.get("pref_roles", {})
compr_def = pref.get("comprador", True)
vend_def  = pref.get("vendedor", False)

# ------------------- UI -------------------
col = st.columns([1,2,1])[1]
with col:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="hdr">🧑‍💻 Alta / Edición de Usuario</div>', unsafe_allow_html=True)

    # ----- Datos básicos -----
    c1, c2 = st.columns(2)
    with c1:
        nombre  = st.text_input("Nombre", key=K("nombre"))
        tipo_doc= st.selectbox("Tipo de Documento", ["DNI","LC","LE","CI","Pasaporte"], index=0, key=K("tipo_doc"))
        dom_env = st.text_input("Domicilio de envío", key=K("dom_env"))
        email   = st.text_input("Email", key=K("email"))
        tel     = st.text_input("Teléfono", key=K("tel"))
    with c2:
        apellido= st.text_input("Apellido", key=K("apellido"))
        nro_doc = st.text_input("N° Documento", key=K("nro_doc"))
        dom_ent = st.text_input("Domicilio de entrega", key=K("dom_ent"))
        cuit    = st.text_input("CUIT (solo visual, no se guarda aún)", key=K("cuit"))
        cuil    = st.text_input("CUIL (solo visual, no se guarda aún)", key=K("cuil"))

    st.markdown('<div class="divisor"></div>', unsafe_allow_html=True)

    # ----- Documentación KYC -----
    st.markdown('<span class="lbl">Adjuntar documentación</span>', unsafe_allow_html=True)
    kyc_files = st.file_uploader(
        "Subí DNI/CUIT/comprobante (1 o más)",
        type=["png","jpg","jpeg","pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        key=K("kyc")
    )

    st.markdown('<div class="divisor"></div>', unsafe_allow_html=True)

    # ----- Seguridad & Acceso -----
    c3, c4 = st.columns(2)
    with c3:
        palabra_seg = st.text_input("Palabra de seguridad", key=K("palabra"))
        password    = st.text_input("Contraseña", type="password", key=K("password"))
    with c4:
        alias_cbu = st.text_input("CBU/CBU Alias (banco)", key=K("cbu"))
        wallet    = st.text_input("Wallet pública (cripto)", key=K("wallet"))
        red       = st.selectbox("Red", ["BEP20","ERC20","TRC20","Polygon","Arbitrum"], index=0, key=K("red"))

    st.caption("Estos datos bancarios/cripto se usarán para generar QR y recibir pagos. "
               "El usuario es responsable de su validez.")

    st.markdown('<div class="divisor"></div>', unsafe_allow_html=True)

    # ----- Roles (multi) -----
    st.markdown("**Roles del usuario** (podés marcar uno o ambos):")
    comprador_ck = st.checkbox("COMPRADOR", value=compr_def, key=K("role_compr"))
    vendedor_ck  = st.checkbox("VENDEDOR",  value=vend_def,  key=K("role_vend"))
    # ADMIN NO aparece en la UI

    st.markdown('<div class="divisor"></div>', unsafe_allow_html=True)

    # ----- Términos -----
    acepto = st.checkbox("Acepto los términos de uso y privacidad", key=K("acepto"))

    st.markdown('<div class="divisor"></div>', unsafe_allow_html=True)

    # ----- Botones -----
    colA, colB, colC, colD = st.columns(4)

    with colA:
        if st.button("REGISTRAR", use_container_width=True, key=K("btn_reg")):
            if not (nombre and apellido and email and nro_doc and password and acepto):
                st.error("Completá: Nombre, Apellido, Email, Documento, Contraseña y aceptá Términos.")
            else:
                payload = _build_payload(
                    nombre, apellido, tipo_doc, nro_doc, email, tel,
                    palabra_seg, password, acepto,
                    dom_env, dom_ent, alias_cbu, wallet, red,
                    comprador_ck, vendedor_ck
                )
                # Reglas visibles antes de enviar
                if "COMPRADOR" in payload["roles"] and not payload["domicilio_entrega"]:
                    st.warning("COMPRADOR requiere domicilio de ENTREGA.")
                elif "VENDEDOR" in payload["roles"] and (payload["banking"] is None or not payload["wallets"]):
                    st.warning("VENDEDOR requiere CBU/Alias y al menos una Wallet.")
                else:
                    try:
                        r = _post_user(payload)
                        if r.status_code == 201:
                            data = r.json()
                            st.session_state["last_user_id"] = data["id"]
                            st.success(f"Usuario creado ✅ ID: {data['id']}")
                        else:
                            st.error(f"Error {r.status_code}: {r.text}")
                    except Exception as e:
                        st.error(f"Fallo conexión: {e}")

    with colB:
        if st.button("ACTUALIZAR", use_container_width=True, key=K("btn_upd")):
            uid = st.session_state.get("last_user_id")
            if not uid:
                st.warning("No hay usuario en sesión. Primero creá uno.")
            else:
                payload = _build_payload(
                    nombre, apellido, tipo_doc, nro_doc, email, tel,
                    palabra_seg, password, acepto,
                    dom_env, dom_ent, alias_cbu, wallet, red,
                    comprador_ck, vendedor_ck
                )
                try:
                    r = _put_user(uid, payload)
                    if r.status_code == 200:
                        st.success("Usuario actualizado ✅")
                    else:
                        st.error(f"Error {r.status_code}: {r.text}")
                except Exception as e:
                    st.error(f"Fallo conexión: {e}")

    with colC:
        if st.button("SUBIR KYC", use_container_width=True, key=K("btn_kyc")):
            uid = st.session_state.get("last_user_id")
            if not uid:
                st.warning("Primero creá el usuario para tener un ID.")
            elif not kyc_files:
                st.warning("Subí uno o más archivos.")
            else:
                try:
                    r = _upload_kyc(uid, kyc_files)
                    if r.status_code == 200:
                        st.success("KYC subido ✅")
                    else:
                        st.error(f"Error {r.status_code}: {r.text}")
                except Exception as e:
                    st.error(f"Fallo conexión: {e}")

    with colD:
        if st.button("LIMPIAR", use_container_width=True, key=K("btn_clean")):
            _limpieza_rapida()
            st.session_state["last_user_id"] = None
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ---- Ayuda contextual ----
with st.expander("ℹ️ Requisitos por rol"):
    st.write("""
- **COMPRADOR**
  - Datos personales, email y contraseña
  - **Domicilio de entrega** (obligatorio)
  - Aceptar Términos y Privacidad

- **VENDEDOR**
  - Todo lo anterior
  - **CBU/Alias bancario** y **Wallet pública** (obligatorio)
  - Adjuntar documentos **KYC** (DNI/CUIT/comprobante)

- **ADMIN**
  - No se auto-asigna desde esta pantalla. Solo puede asignarse desde JSON/Backend.
""")
