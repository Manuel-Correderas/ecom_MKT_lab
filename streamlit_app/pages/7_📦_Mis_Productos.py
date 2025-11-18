# streamlit_app/pages/7_📦_Mis_Productos.py
import os
import requests
import streamlit as st

st.set_page_config(page_title="Mis Productos (Vendedor)", layout="centered")

BACKEND_URL   = os.getenv("BACKEND_URL", "http://localhost:8000")
SELLER_ID     = st.session_state.get("seller_id", "hm-1")
SELLER_ALIAS  = st.session_state.get("seller_alias", "H&M")

def pesos(n: int | float) -> str:
    try:
        return f"${int(n):,}".replace(",", ".")
    except Exception:
        return f"${n}"

def fetch_my_products():
    try:
        r = requests.get(f"{BACKEND_URL}/products", params={"seller_id": SELLER_ID}, timeout=10)
        if r.status_code == 200:
            return r.json()
        st.warning(f"No pude cargar productos (HTTP {r.status_code}).")
        return []
    except requests.RequestException:
        st.error("No se pudo conectar al backend. ¿Está corriendo en :8000?")
        return []

def update_product(prod_id: str, payload: dict):
    try:
        r = requests.put(f"{BACKEND_URL}/products/{prod_id}", json=payload, timeout=10)
        if r.status_code == 200:
            st.success("✅ Producto actualizado.")
            st.rerun()
        else:
            st.error(f"Error al actualizar (HTTP {r.status_code})")
    except requests.RequestException:
        st.error("No se pudo conectar al backend.")

def delete_product(prod_id: str):
    try:
        r = requests.delete(f"{BACKEND_URL}/products/{prod_id}", timeout=10)
        if r.status_code in (200, 204):
            st.success("🗑 Producto eliminado.")
            st.rerun()
        else:
            st.error(f"Error al eliminar (HTTP {r.status_code})")
    except requests.RequestException:
        st.error("No se pudo conectar al backend.")

def create_product(payload: dict):
    try:
        r = requests.post(f"{BACKEND_URL}/products", json=payload, timeout=10)
        if r.status_code in (200, 201):
            st.success("✅ Producto creado.")
            st.rerun()
        else:
            st.error(f"Error al crear (HTTP {r.status_code})")
    except requests.RequestException:
        st.error("No se pudo conectar al backend.")

# ------------- estilos -------------
st.markdown("""
<style>
.stApp { background:#FF8C00; }
.panel{background:#f79b2f;border-radius:14px;padding:16px 18px;box-shadow:0 8px 18px rgba(0,0,0,.18);}
.hdr{text-align:center;font-weight:900;letter-spacing:.6px;color:#10203a;margin-bottom:10px;}
.sub{color:#162c56;font-size:.92rem;}
.list{background:#ffa84d;border-radius:10px;padding:10px;margin-top:8px;max-height:460px;overflow-y:auto;box-shadow: inset 0 1px 4px rgba(0,0,0,.12);}
.card{background:#fff5e6;border-radius:10px;padding:12px;box-shadow:0 2px 8px rgba(0,0,0,.12);margin-bottom:10px;}
.small{font-size:.86rem;color:#333;}
.btn-primary{background:#0b3a91 !important;color:#fff !important;border:none !important;border-radius:8px !important;padding:8px 14px !important;font-weight:900 !important;}
.btn-secondary{background:#936037 !important;color:#fff !important;border:none !important;border-radius:8px !important;padding:8px 14px !important;font-weight:900 !important;}
.btn-danger{background:#c0392b !important;color:#fff !important;border:none !important;border-radius:8px !important;padding:8px 14px !important;font-weight:900 !important;}
.seller-header{background:#ff9b2f;padding:12px;border-radius:8px;margin-bottom:15px;text-align:center;}
</style>
""", unsafe_allow_html=True)

# ------------- cabecera -------------
st.markdown('<div class="hdr"><h3>📦 MIS PRODUCTOS</h3></div>', unsafe_allow_html=True)
st.markdown('<div class="panel">', unsafe_allow_html=True)

# Información del vendedor
st.markdown("<div class='seller-header'>", unsafe_allow_html=True)
st.markdown(f"### 🏪 {SELLER_ALIAS} - VENDEDOR")
st.caption(f"ID vendedor: `{SELLER_ID}`")
st.markdown("</div>", unsafe_allow_html=True)

# Config vendedor
st.markdown("### ⚙️ CONFIGURACIÓN DE VENDEDOR")
col_alias, col_logo = st.columns([2, 2])
with col_alias:
    new_alias = st.text_input("Alias de vendedor", value=SELLER_ALIAS, placeholder="Nombre de tu tienda", key="alias_input")
with col_logo:
    logo_url = st.text_input("URL del logo (opcional)", placeholder="https://ejemplo.com/logo.png", key="logo_input")

if new_alias != SELLER_ALIAS:
    st.session_state["seller_alias"] = new_alias
    st.info("Alias actualizado para la sesión (los productos nuevos saldrán con este alias).")

# ------------- lista de productos -------------
st.markdown("### 🛍️ MIS PRODUCTOS PUBLICADOS")
st.markdown('<div class="list">', unsafe_allow_html=True)

products = fetch_my_products()

if not products:
    st.info("Todavía no tenés productos publicados.")
else:
    for p in products:
        pid = p["id"]
        st.markdown('<div class="card">', unsafe_allow_html=True)

        # header
        h1, h2, h3 = st.columns([4, 1, 1])
        with h1:
            st.markdown(f"**{p.get('name','(sin nombre)')}**")
            st.caption(f"📂 {p.get('category','-')} • 🔍 {p.get('subcategory','-')}")
        with h2:
            img = p.get("image_url")
            if img:
                try:
                    st.image(img, use_container_width=True)
                except Exception:
                    st.markdown(
                        '<div style="background:#f8f9fa;border-radius:8px;padding:20px;text-align:center;border:1px solid #ddd;">📸</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.markdown(
                    '<div style="background:#f8f9fa;border-radius:8px;padding:20px;text-align:center;border:1px solid #ddd;">📸</div>',
                    unsafe_allow_html=True
                )
        with h3:
            st.markdown(f"**⭐ {p.get('rating',0):.1f}**")
            st.markdown(f"**🎯 {p.get('sold',0)} vendidos**")

        # formulario de edición por producto (evita keys duplicadas)
        with st.form(key=f"frm_{pid}"):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Nombre", value=p.get("name",""), key=f"name_{pid}")
                category = st.text_input("Categoría", value=p.get("category",""), key=f"cat_{pid}")
                subcategory = st.text_input("Subcategoría", value=p.get("subcategory",""), key=f"sub_{pid}")
            with c2:
                price = st.number_input("Precio", value=int(p.get("price",0)), min_value=0, key=f"price_{pid}")
                stock = st.number_input("Stock", value=int(p.get("stock",0)), min_value=0, key=f"stock_{pid}")
                image_url = st.text_input("URL imagen", value=p.get("image_url",""), key=f"img_{pid}")

            description = st.text_area("Descripción", value=p.get("description",""), key=f"desc_{pid}")
            features = st.text_area("Características (multilínea)", value=p.get("features",""), key=f"feat_{pid}")

            u1, u2, u3 = st.columns(3)
            with u1:
                submit = st.form_submit_button("💾 GUARDAR CAMBIOS", use_container_width=True)
            with u2:
                del_click = st.form_submit_button("🗑 ELIMINAR", use_container_width=True)
            with u3:
                st.caption(f"ID: {pid}")

            if submit:
                payload = {
                    "name": name,
                    "category": category,
                    "subcategory": subcategory,
                    "price": int(price),
                    "stock": int(stock),
                    "image_url": image_url or None,
                    "description": description or None,
                    "features": features or None,
                    "seller_id": SELLER_ID,
                    "seller_alias": st.session_state.get("seller_alias", SELLER_ALIAS),
                }
                update_product(pid, payload)

            if del_click:
                delete_product(pid)

        st.markdown("</div>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # /list

# ------------- agregar nuevo producto -------------
st.markdown("### ➕ AGREGAR NUEVO PRODUCTO")
with st.form("nuevo_producto"):
    c1, c2 = st.columns(2)
    with c1:
        new_name = st.text_input("Nombre del producto", key="new_name")
        new_category = st.text_input("Categoría", key="new_category")
        new_subcategory = st.text_input("Subcategoría", key="new_subcategory")
    with c2:
        new_price = st.number_input("Precio unitario", min_value=0, value=0, key="new_price")
        new_stock = st.number_input("Stock inicial", min_value=0, value=0, key="new_stock")
        new_image = st.text_input("URL de imagen", key="new_image")

    new_description = st.text_area("Descripción breve", key="new_description")
    new_features = st.text_area("Características", key="new_features")

    col_submit, col_clear = st.columns(2)
    with col_submit:
        submitted = st.form_submit_button("✅ AGREGAR PRODUCTO", use_container_width=True)
    with col_clear:
        st.form_submit_button("🔄 LIMPIAR FORMULARIO", use_container_width=True)

if 'submitted' in locals() and submitted:
    if not new_name:
        st.error("El nombre es obligatorio.")
    else:
        payload = {
            "name": new_name,
            "price": int(new_price),
            "stock": int(new_stock),
            "category": new_category or None,
            "subcategory": new_subcategory or None,
            "image_url": new_image or None,
            "description": new_description or None,
            "features": new_features or None,
            "seller_id": SELLER_ID,
            "seller_alias": st.session_state.get("seller_alias", SELLER_ALIAS),
            "rating": 0.0,
            "sold": 0
        }
        create_product(payload)

# Volver
st.write("")
st.button("⬅️ VOLVER AL PANEL", key="btn_back_products", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)
