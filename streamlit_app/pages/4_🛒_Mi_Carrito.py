# streamlit_app/pages/4_🛒_Mi_Carrito.py
import time
import streamlit as st
import requests
from auth_helpers import get_backend_url, auth_headers, require_login

st.set_page_config(page_title="Mi Carrito - Ecom MKT Lab", layout="centered")

BACKEND_URL = get_backend_url()
PAGE_NS = "cart_v1"
def K(s: str) -> str: return f"{PAGE_NS}:{s}"

# Aseguramos login
if not require_login():
    st.stop()

# ===== estilos =====
st.markdown("""
<style>
.stApp { background:#FF8C00; }
.cart-panel{
  background:#f79b2f; border-radius:12px; padding:16px 18px;
  box-shadow:0 8px 18px rgba(0,0,0,.18);
}
.hdr { text-align:center; font-weight:900; letter-spacing:.5px;
  color:#113; margin-bottom:12px; font-size:1.1rem; }
.item{
  background:#fff5e6; border-radius:10px; padding:12px 12px;
  box-shadow:0 2px 8px rgba(0,0,0,.12); margin-bottom:10px;
}
.item .title{ font-weight:800; color:#1f2e5e; margin-bottom:4px; }
.item .meta { font-size:.9rem; color:#222; line-height:1.15rem; }
.badge-total{ display:inline-block; background:#d6d6d6; color:#000; font-weight:900;
  border-radius:8px; padding:6px 10px; margin:6px 0; }
.controls{ display:flex; gap:8px; align-items:center; justify-content:flex-end; }
.controls button{ background:#0b3a91; color:#fff; border:none; border-radius:8px; padding:6px 10px; font-weight:800; }
.controls .danger{ background:#c0392b; }
.footer-btn{ background:#0b3a91; color:#fff; border:none; border-radius:8px; padding:10px 18px; font-weight:900; }
.footer-btn.secondary{ background:#936037; }
</style>
""", unsafe_allow_html=True)

# ===== helpers backend =====
def get_cart():
    r = requests.get(f"{BACKEND_URL}/cart", headers=auth_headers(), timeout=15)
    if r.status_code == 200:
        return r.json()
    st.error(f"No se pudo cargar el carrito (HTTP {r.status_code})")
    try:
        st.json(r.json())
    except Exception:
        st.write(r.text)
    st.stop()

def patch_item(item_id: str, qty: int) -> bool:
    r = requests.patch(
        f"{BACKEND_URL}/cart/items/{item_id}",
        json={"qty": qty},
        headers=auth_headers(),
        timeout=15,
    )
    if r.status_code not in (200, 204):
        st.error(f"No se pudo actualizar cantidad (HTTP {r.status_code}): {r.text}")
        return False
    return True

def remove_item(item_id: str) -> bool:
    r = requests.delete(
        f"{BACKEND_URL}/cart/items/{item_id}",
        headers=auth_headers(),
        timeout=15,
    )
    if r.status_code not in (200, 204):
        st.error(f"No se pudo quitar el ítem (HTTP {r.status_code}): {r.text}")
        return False
    return True

def checkout():
    r = requests.post(
        f"{BACKEND_URL}/orders/checkout",
        headers=auth_headers(),
        timeout=30,
    )
    ok = r.status_code == 201
    data = None
    try:
        data = r.json()
    except Exception:
        data = r.text
    return ok, data

# ===== data =====
cart = get_cart()
items = cart.get("items", []) if isinstance(cart, dict) else cart
if not items:
    st.markdown("## 🛒 Mi Carrito")
    st.info("Tu carrito está vacío.")
    st.stop()

total_general = 0

st.markdown('<div class="hdr">🛒 MI CARRITO</div>', unsafe_allow_html=True)
st.markdown('<div class="cart-panel">', unsafe_allow_html=True)

for idx, item in enumerate(items):
    cart_item_id = str(item.get("id"))
    name = item.get("name", "Producto")
    seller = item.get("seller", "Vendedor")
    rating = item.get("rating", 0)
    category = item.get("category", "")
    subcategory = item.get("subcategory", "")
    stock = int(item.get("stock", item.get("stock_snapshot", 1) or 1))
    qty = int(item.get("qty", 1))
    price = float(item.get("price", 0))
    image = item.get("image")

    subtotal = qty * price
    total_general += subtotal

    with st.container():
        st.markdown('<div class="item">', unsafe_allow_html=True)
        st.markdown(f'<div class="title">{name}</div>', unsafe_allow_html=True)

        colL, colM, colR = st.columns([3,1,2])
        with colL:
            st.markdown(
                f"""<div class="meta">
                <b>VENDEDOR:</b> {seller} &nbsp;&nbsp; <b>VALORACIÓN:</b> {rating}/10<br>
                <b>CATEGORÍA:</b> {category}<br>
                <b>SUBCATEGORÍA:</b> {subcategory}<br>
                <b>STOCK:</b> {stock}<br>
                <b>PRECIO UNITARIO:</b> ${price:,.0f}
                </div>""".replace(",", "."),
                unsafe_allow_html=True
            )
            st.markdown(
                f'<span class="badge-total">SUBTOTAL: ${subtotal:,.0f}</span>'.replace(",", "."),
                unsafe_allow_html=True
            )

        with colM:
            if image:
                st.image(image, use_container_width=True)
            else:
                st.markdown(
                    '<div style="background:#f8f9fa; border-radius:8px; padding:40px 20px; text-align:center; border:1px solid #ddd;">'
                    '<span style="color:#666;">📸</span>'
                    '</div>',
                    unsafe_allow_html=True
                )

        with colR:
            st.markdown('<div class="controls">', unsafe_allow_html=True)

            c_sub, c_qty, c_add = st.columns([1,1,1])
            with c_sub:
                if st.button("−", key=K(f"sub_{idx}")):
                    new_qty = max(1, qty - 1)
                    if patch_item(cart_item_id, new_qty):
                        st.rerun()
            with c_qty:
                st.write(f"**{qty}**")
            with c_add:
                if st.button("+", key=K(f"add_{idx}")):
                    new_qty = min(stock, qty + 1)
                    if patch_item(cart_item_id, new_qty):
                        st.rerun()

            st.write("")
            if st.button("🗑 Quitar", key=K(f"rm_{idx}")):
                if remove_item(cart_item_id):
                    st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
        st.divider()

st.markdown("</div>", unsafe_allow_html=True)

st.subheader(f"💰 TOTAL A PAGAR: ${total_general:,.0f}".replace(",", "."))

# 👇 dejá todo lo demás igual, SOLO cambiá este bloque
col1, col2 = st.columns(2)
with col1:
    if st.button("💳 PAGAR", key=K("pay"), use_container_width=True):
        # En lugar de llamar al backend, vamos a la pantalla de checkout
        try:
            st.switch_page("pages/10_💳_Checkout.py")
        except Exception:
            st.info("Abrí la página de 'Checkout' desde el menú lateral.")

with col2:
    if st.button("⬅️ VOLVER", key=K("back"), use_container_width=True):
        st.switch_page("Home.py")


with st.expander("📦 Información de Compra"):
    st.markdown("""
    **Métodos de pago aceptados:**
    - 💳 Tarjetas de crédito/débito  
    - 🏦 Transferencia bancaria  
    - ₿ Criptomonedas  
    - 📱 Mercado Pago  
    
    **Envío:** Gratis en compras mayores a $30.000  
    **Tiempo de entrega:** 3-5 días hábiles
    """)
