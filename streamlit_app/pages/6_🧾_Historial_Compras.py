# streamlit_app/pages/6_🧾_Historial_Compras.py
import os
import requests
import streamlit as st

st.set_page_config(page_title="Historial de Compras (Cliente)", layout="centered")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
USER_ID = st.session_state.get("user_id", "cli-a")
USER_NAME = st.session_state.get("user_name", "Cliente A")

def pesos(n: int | float) -> str:
    try:
        return f"${int(n):,}".replace(",", ".")
    except Exception:
        return f"${n}"

def fetch_orders(user_id: str):
    try:
        r = requests.get(f"{BACKEND_URL}/orders", params={"user_id": user_id}, timeout=10)
        if r.status_code == 200:
            return r.json()
        st.warning(f"No pude cargar órdenes (HTTP {r.status_code}).")
        return []
    except requests.RequestException:
        st.error("No se pudo conectar al backend. ¿Está corriendo en :8000?")
        return []

# ================== Estilos ==================
st.markdown("""<style>
.stApp { background:#FF8C00; }
.panel{background:#f79b2f;border-radius:14px;padding:16px 18px;box-shadow:0 8px 18px rgba(0,0,0,.18);}
.hdr{text-align:center;font-weight:900;letter-spacing:.6px;color:#10203a;margin-bottom:12px;}
.badge{display:inline-block;background:#d6d6d6;color:#000;font-weight:900;border-radius:8px;padding:6px 10px;margin:4px 0;}
.list{background:#ffa84d;border-radius:10px;padding:10px;margin-top:8px;max-height:460px;overflow-y:auto;box-shadow: inset 0 1px 4px rgba(0,0,0,.12);}
.card{background:#fff5e6;border-radius:10px;padding:12px;box-shadow:0 2px 8px rgba(0,0,0,.12);margin-bottom:10px;}
.small{font-size:.86rem;color:#333;}
.btn-primary{background:#0b3a91 !important;color:#fff !important;border:none !important;border-radius:8px !important;padding:8px 14px !important;font-weight:900 !important;}
.btn-secondary{background:#936037 !important;color:#fff !important;border:none !important;border-radius:8px !important;padding:8px 14px !important;font-weight:900 !important;}
.client-header{background:#ff9b2f;padding:12px;border-radius:8px;margin-bottom:15px;text-align:center;}
</style>""", unsafe_allow_html=True)

# ================== Encabezado ==================
st.markdown('<div class="hdr"><h3>🧾 HISTORIAL DE COMPRAS</h3></div>', unsafe_allow_html=True)
st.markdown('<div class="panel">', unsafe_allow_html=True)

# Traer órdenes
orders = fetch_orders(USER_ID)

# Cabecera cliente + resumen
total_gasto = sum(o.get("total_amount", 0) for o in orders)
st.markdown("<div class='client-header'>", unsafe_allow_html=True)
st.markdown(f"### 👤 {USER_NAME}")
st.markdown(f"**📊 RESUMEN:** {len(orders)} COMPRAS • 💵 {pesos(total_gasto)} TOTAL GASTADO")
st.markdown("</div>", unsafe_allow_html=True)

# Búsqueda y filtros
st.markdown("### 🔍 BUSCAR EN MIS COMPRAS")
col_search, col_filter = st.columns([3, 1])
with col_search:
    search_query = st.text_input("", placeholder="Buscar por producto, empresa o vendedor...")
with col_filter:
    filter_status = st.selectbox("Estado", ["Todas", "Entregado", "En camino", "Pendiente"])

# ================== Lista de Compras ==================
st.markdown('<div class="list">', unsafe_allow_html=True)

def order_matches(o: dict) -> bool:
    if filter_status != "Todas" and o.get("status") != filter_status:
        return False
    if not search_query:
        return True
    q = search_query.lower()
    for it in o.get("items", []):
        if any(q in str(x or "").lower() for x in [it.get("product_name"), it.get("seller"), it.get("company")]):
            return True
    return False

filtered = [o for o in orders if order_matches(o)]

if not filtered:
    st.info("No se encontraron compras que coincidan con los filtros.")
else:
    for o in filtered:
        st.markdown('<div class="card">', unsafe_allow_html=True)

        # Si la orden tiene varios ítems, mostramos el primero como “cabecera”
        first = (o.get("items") or [{}])[0]
        product_name = first.get("product_name", "(sin ítems)")
        category = first.get("category") or "-"
        subcategory = first.get("subcategory") or "-"
        seller = first.get("seller") or "-"
        company = first.get("company") or "-"
        status = o.get("status", "-")
        total = o.get("total_amount", 0)
        date_iso = o.get("created_at", "")[:10]  # YYYY-MM-DD
        time_iso = o.get("created_at", "")[11:16]  # HH:MM

        col_header1, col_header2 = st.columns([3, 1])
        with col_header1:
            st.markdown(f"**🛍️ {product_name}**")
            st.caption(f"📂 {category} • 🔍 {subcategory}")
        with col_header2:
            icon = "🟢" if status == "Entregado" else "🟡" if status == "En camino" else "🔴"
            st.markdown(f"**{icon} {status}**")

        col_details1, col_details2 = st.columns(2)
        with col_details1:
            st.markdown(f"""
            **📅 Fecha:** {date_iso} {time_iso}  
            **🏪 Vendedor:** {seller}  
            **🏢 Empresa:** {company}  
            **🧾 Orden:** {o.get("id")}
            """)
        with col_details2:
            try:
                qty_sum = sum(it.get("quantity", 0) for it in o.get("items", []))
            except Exception:
                qty_sum = "-"
            st.markdown(f"""
            **📦 Ítems:** {qty_sum}  
            **💵 Total Orden:** {pesos(total)}  
            **👤 Cliente:** {o.get("user_name") or USER_NAME}
            """)

        st.markdown(f"<span class='badge'>💵 TOTAL: {pesos(total)}</span>", unsafe_allow_html=True)

        # Acciones (placeholder)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.button("📄 Ver Factura", key=f"invoice_{o['id']}")
        with c2:
            st.button("📦 Seguir Envío", key=f"track_{o['id']}")
        with c3:
            st.button("⭐ Valorar", key=f"rate_{o['id']}")

        st.markdown("</div>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # /list

# ================== Pie ==================
st.write("")
st.button("⬅️ VOLVER AL PANEL", key="btn_back_hist", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)  # /panel
