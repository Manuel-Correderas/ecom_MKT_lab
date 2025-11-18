import os
import json
import requests
import pandas as pd
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from auth_helpers import get_backend_url, auth_headers, require_login  # <-- usar helpers

# Cargar variables desde .env (en la raíz del proyecto)
load_dotenv()

st.set_page_config(page_title="Producto - Ecom MKT Lab", layout="centered")

BACKEND_URL = get_backend_url()
PAGE_NS = "producto_v1"
def K(s: str) -> str:
    return f"{PAGE_NS}:{s}"

# ========= helpers carrito / auth =========

def ensure_last_product(prod_id: str):
    st.session_state["last_product"] = prod_id

def require_login_for_cart() -> bool:
    # simple wrapper del helper genérico
    return require_login()

def csv_path():
    for p in [
        Path(__file__).resolve().parents[1] / "data" / "products.csv",
        Path.cwd() / "data" / "products.csv",
        Path(__file__).resolve().parent / "data" / "products.csv",
    ]:
        if p.exists():
            return p
    return None

def load_csv_product(prod_id: str | int) -> dict | None:
    p = csv_path()
    if not p:
        return None
    try:
        df = pd.read_csv(p, encoding="utf-8-sig").fillna("")
        df["id"] = df["id"].astype(str)
        row = df[df["id"] == str(prod_id)]
        if row.empty:
            return None
        r = row.iloc[0].to_dict()
        return {
            "id": str(r.get("id", "")),
            "name": r.get("name", "Producto"),
            "description": r.get("description", ""),
            "price": float(r.get("price", 0) or 0),
            "stock": int(float(r.get("stock", 0) or 0)),
            "condition": "NUEVO",
            "category_id": r.get("category", ""),
            "subcategory": r.get("subcategory", ""),
            "image_url": r.get("image_url", ""),
            "seller_id": "demo",
            "seller_name": r.get("seller", "Demo Seller"),
            "rating": float(r.get("rating", 0) or 0),
            "sold_count": int(float(r.get("sold", 0) or 0)),
            "features": [
                x.strip()
                for x in str(r.get("features", "")).split(";")
                if x.strip()
            ],
            "images": (
                [{"url": r.get("image_url", ""), "sort_order": 0}]
                if str(r.get("image_url", "")).strip()
                else []
            ),
        }
    except Exception:
        return None

def fetch_product_from_backend(prod_id: str) -> dict | None:
    try:
        r = requests.get(f"{BACKEND_URL}/products/{prod_id}", timeout=10)
        if r.status_code == 200:
            return r.json()
        return None
    except Exception:
        return None

def fetch_comments_from_backend(prod_id: str) -> list:
    try:
        r = requests.get(f"{BACKEND_URL}/products/{prod_id}/comments", timeout=10)
        return r.json() if r.status_code == 200 else []
    except Exception:
        return []

def product_image_url(data: dict) -> str | None:
    url = str(data.get("image_url") or "").strip()
    if url.startswith("http://") or url.startswith("https://"):
        return url
    imgs = data.get("images") or []
    if isinstance(imgs, list) and imgs:
        first = imgs[0]
        if isinstance(first, dict):
            u = str(first.get("url", "")).strip()
            if u.startswith("http://") or u.startswith("https://"):
                return u
        else:
            u = str(first).strip()
            if u.startswith("http://") or u.startswith("https://"):
                return u
    return None

# ===== estilos =====
st.markdown("""
<style>
.stApp { background:#FF8C00; }
.panel { background:#ffffff; padding:20px; border-radius:12px; box-shadow: 0 8px 20px rgba(0,0,0,0.15); }
.product-header { background:#ff9b2f; padding:15px; border-radius:10px; margin-bottom:20px; }
.box { background:#f8f9fa; padding:12px; border-radius:8px; margin-top:12px; border-left: 4px solid #0b3a83; }
.badge{ background:#0b3a83; color:#fff; border-radius:8px; padding:4px 10px; font-weight:700; font-size:0.9rem; }
.price{ color:#0b3a83; font-weight:900; font-size:1.5rem; }
.rating { color:#ffc107; font-weight:bold; }
.seller { color:#936037; font-weight:bold; }
</style>
""", unsafe_allow_html=True)

# ===== navegación =====
top = st.columns([1, 6, 1])
with top[0]:
    if st.button("⬅️", key=K("btn_back"), help="Volver al Home"):
        st.switch_page("Home.py")
with top[1]:
    st.markdown("### 🧥 Detalle del Producto")
with top[2]:
    st.markdown("<div class='badge'>Ecom MKT Lab</div>", unsafe_allow_html=True)

# ===== identificar producto =====
qp = st.query_params
product_id = qp.get("id") or st.session_state.get("last_product")

if not product_id:
    st.warning("Falta el parámetro ?id=<product_id> y no hay selección previa.")
    st.page_link("Home.py", label="⬅ Volver al Home")
    st.stop()

product_id = str(product_id)
ensure_last_product(product_id)

# ===== cargar producto (backend -> csv) =====
from_backend = True
data = fetch_product_from_backend(product_id)
if data is None:
    from_backend = False
    data = load_csv_product(product_id)
    if data is None:
        st.error("No se encontró el producto (ni en backend ni en CSV).")
        st.page_link("Home.py", label="⬅ Volver al Home")
        st.stop()
    else:
        st.info("El backend no respondió. Mostrando datos desde CSV (carrito deshabilitado).")

# ===== comentarios (backend -> demo) =====
comments = fetch_comments_from_backend(product_id)
if not comments:
    comments = [
        {"rating": 5, "user_name": "María", "text": "Excelente calidad 👌"},
        {"rating": 4, "user_name": "Juan", "text": "Buena relación precio/calidad"},
    ]

# ===== normalizar campos esperados =====
product_name = data.get("name", "Producto")
condition = data.get("condition", "NUEVO")
sold_base = data.get("sold_count", 0)
stock_base = data.get("stock", 0)
rating = data.get("rating", 0.0)
seller = data.get("seller_name", "Vendedor")
price = data.get("price", 0)
description = data.get("description", "Sin descripción")
image_url = product_image_url(data)

# ===== STOCK DIRECTO DESDE BACKEND/CSV (sin restar lo del carrito) =====
try:
    stock_count = int(stock_base)
except Exception:
    stock_count = 0

# ===== panel =====
st.markdown("<div class='panel'>", unsafe_allow_html=True)
col_img, col_info = st.columns([1, 1])

with col_img:
    st.markdown("### 📸")
    if image_url:
        st.image(image_url, use_container_width=True)
    else:
        st.markdown(
            '<div style="background:#f8f9fa; border-radius:10px; padding:60px; text-align:center; border:2px dashed #ddd;">'
            '<span style="color:#666;">Imagen del Producto</span>'
            '</div>',
            unsafe_allow_html=True,
        )

with col_info:
    st.markdown("<div class='product-header'>", unsafe_allow_html=True)
    st.markdown(f"### {product_name}")
    st.markdown(
        f"**Estado:** {condition} • **Vendidos:** {sold_base} • **Stock disponible:** {stock_count}"
    )
    st.markdown("</div>", unsafe_allow_html=True)

    try:
        price_str = f"$ {float(price):,.0f}".replace(",", ".")
    except Exception:
        price_str = "$ --"

    st.markdown(f"<div class='price'>{price_str}</div>", unsafe_allow_html=True)
    st.markdown(
        f"<span class='rating'>⭐ {rating}/10</span> | "
        f"<span class='seller'>🏪 {seller}</span>",
        unsafe_allow_html=True,
    )

    # ==== CONTROLES DE COMPRA: CANTIDAD + AÑADIR AL CARRITO ====
    if from_backend:
        max_qty = max(1, stock_count) if stock_count > 0 else 1
        qty = st.number_input(
            "Cantidad",
            min_value=1,
            max_value=max_qty,
            value=1,
            step=1,
            key=K("qty"),
        )

        if st.button("🛒 Añadir al carrito", key=K("add_cart")):
            if not require_login_for_cart():
                st.stop()

            if stock_count <= 0:
                st.error("No hay stock disponible para este producto.")
            else:
                try:
                    r = requests.post(
                        f"{BACKEND_URL}/cart/items",
                        json={"product_id": product_id, "qty": int(qty)},
                        headers=auth_headers(),
                        timeout=15,
                    )
                    if r.status_code in (200, 201):
                        st.success("Producto añadido al carrito ✅")
                        # Si querés refrescar por si cambian datos en backend
                        if hasattr(st, "rerun"):
                            st.rerun()
                        else:
                            st.experimental_rerun()
                    else:
                        st.error(
                            f"Error al agregar al carrito (HTTP {r.status_code}): {r.text}"
                        )
                except Exception as e:
                    st.error(f"No se pudo conectar al backend: {e}")
    else:
        st.info("Para agregar al carrito se requiere conexión al backend.")

    st.markdown("<div class='box'>**📝 Descripción**</div>", unsafe_allow_html=True)
    st.write(description)

    st.markdown("<div class='box'>**🔍 Características**</div>", unsafe_allow_html=True)
    features = data.get("features") or []
    if isinstance(features, (list, tuple)) and features:
        for f in features:
            st.write(f"- {f}")
    else:
        st.caption("Sin características adicionales.")

    st.markdown("<div class='box'>**💬 Comentarios y Valoraciones**</div>", unsafe_allow_html=True)
    if comments:
        for c in comments[:5]:
            try:
                stars = "⭐" * int(round(float(c.get("rating", 0))))
            except Exception:
                stars = ""
            user = c.get("user_name") or c.get("user_id", "Usuario")
            txt = c.get("text", "")
            st.write(f"{stars} *{txt}* — {user}")
    else:
        st.caption("No hay comentarios todavía.")

st.markdown("</div>", unsafe_allow_html=True)

with st.expander("📦 Información de Envío y Devoluciones"):
    st.markdown("""
    **🚚 Envíos a todo el país**
    - Gratis en compras mayores a $30.000  
    - Entrega en 3-5 días hábiles  
    - Seguimiento online incluido  
    
    **↩️ Devoluciones**
    - 30 días para cambios y devoluciones  
    - Producto debe estar en perfecto estado  
    - El costo de envío corre por el cliente  
    """)
