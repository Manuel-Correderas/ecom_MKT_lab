# streamlit_app/pages/5b_📖_Ver_Comentarios.py
import os
import json
import requests
import pandas as pd
from ast import literal_eval
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="Ver comentarios", layout="centered")

# ----------------- Config -----------------
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "comments.csv"
DATA_PATH.parent.mkdir(parents=True, exist_ok=True)

# Tomamos product_id de la URL (?id=...) o default 1
qp = st.query_params
PRODUCT_ID = str(qp.get("id", "1"))

def load_comments(product_id: str) -> list[dict]:
    # 1) Intento backend
    try:
        r = requests.get(f"{BACKEND_URL}/comments", params={"product_id": product_id}, timeout=8)
        if r.status_code == 200:
            data = r.json() or []
            # Normalizar claves por si el backend usa otros nombres
            normalized = []
            for it in data:
                normalized.append({
                    "user": it.get("user_name", "Anónimo"),
                    "rating": float(it.get("rating", 0.0)),
                    "comment": it.get("comment", ""),
                    "date": it.get("date") or it.get("created_at", "")[:10],
                    "criteria": it.get("criteria", {}),
                })
            return normalized
    except Exception:
        pass

    # 2) Fallback CSV
    if DATA_PATH.exists():
        try:
            df = pd.read_csv(DATA_PATH)
            df = df[df["product_id"].astype(str) == str(product_id)]
            reviews = []
            for _, row in df.iterrows():
                crit_raw = row.get("criteria", "{}")
                try:
                    # puede estar serializado como str(dict) o JSON
                    criteria = literal_eval(crit_raw)
                except Exception:
                    try:
                        criteria = json.loads(crit_raw)
                    except Exception:
                        criteria = {}
                reviews.append({
                    "user": row.get("user_name", "Anónimo"),
                    "rating": float(row.get("rating", 0.0)),
                    "comment": row.get("comment", ""),
                    "date": row.get("date", ""),
                    "criteria": criteria,
                })
            return reviews
        except Exception as e:
            st.warning(f"No se pudo leer comments.csv: {e}")

    return []

# ----------------- Estilos -----------------
st.markdown("""
<style>
.stApp { background:#FF8C00; }
.wrap{
  background:#f79b2f; border-radius:14px; padding:16px 18px;
  box-shadow:0 8px 18px rgba(0,0,0,.18);
}
.hdr{ text-align:center; font-weight:900; letter-spacing:.6px; color:#10203a; margin-bottom:8px; }
.sub{ font-size:.92rem; color:#162c56; }
.badge{ display:inline-block; background:#d6d6d6; color:#000; font-weight:900; border-radius:8px; padding:6px 10px; margin:6px 0; }
.list{ background:#ffa84d; border-radius:10px; padding:10px; margin-top:8px; max-height: 420px; overflow-y: auto; box-shadow: inset 0 1px 4px rgba(0,0,0,.12); }
.card{ background:#fff5e6; border-radius:10px; padding:10px 12px; box-shadow:0 2px 6px rgba(0,0,0,.12); margin-bottom:10px; }
.card .meta{ color:#333; font-size:.85rem; }
.card .score{ font-weight:900; color:#0b3a91; }
.product-header { background:#ff9b2f; padding:12px; border-radius:8px; margin-bottom:15px; }
</style>
""", unsafe_allow_html=True)

# ----------------- Cabecera -----------------
st.markdown('<div class="hdr"><h3>📖 VER COMENTARIOS</h3></div>', unsafe_allow_html=True)
st.markdown('<div class="wrap">', unsafe_allow_html=True)

# (Demo) Info de producto – si querés, cargalo del backend /products/{id}
product_info = {
    "name": f"Producto {PRODUCT_ID}",
    "seller": "Vendedor",
    "rating": 0.0,
    "category": "-",
    "subcategory": "-"
}

c1, c2 = st.columns([4,1])
with c1:
    st.markdown("<div class='product-header'>", unsafe_allow_html=True)
    st.write(f"**📦 PRODUCTO:** {product_info['name']}  \n**ID:** {PRODUCT_ID}")
    st.markdown(
        f"<div class='sub'>"
        f"<b>🏪 VENDEDOR:</b> {product_info['seller']} • "
        f"<b>⭐ VALORACIÓN:</b> {product_info['rating']}/10<br>"
        f"<b>📂 CATEGORÍA:</b> {product_info['category']}<br>"
        f"<b>🔍 SUBCATEGORÍA:</b> {product_info['subcategory']}"
        f"</div>", 
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)
with c2:
    st.markdown(
        '<div style="background:#f8f9fa; border-radius:8px; padding:40px 20px; text-align:center; border:1px solid #ddd;">'
        '<span style="color:#666;">📸</span>'
        '</div>', 
        unsafe_allow_html=True
    )

# ----------------- Datos -----------------
reviews = load_comments(PRODUCT_ID)

# Métricas generales (si hay datos)
if reviews:
    avg_rating = round(sum(r["rating"] for r in reviews) / len(reviews), 1)
    total_reviews = len(reviews)
    st.markdown(
        f"<span class='badge'>📊 PUNTUACIÓN PROMEDIO: {avg_rating}/10 · {total_reviews} VALORACIONES</span>",
        unsafe_allow_html=True
    )
else:
    st.info("No hay comentarios registrados para este producto.")

# ----------------- Filtros -----------------
st.markdown("### 🔍 FILTRAR COMENTARIOS")
col_filter1, col_filter2, col_filter3 = st.columns([2,2,2])
with col_filter1:
    min_score = st.slider("Puntuación mínima", 0.0, 10.0, 0.0, 0.5)
with col_filter2:
    search_text = st.text_input("Buscar en comentarios", "")
with col_filter3:
    sort_order = st.toggle("Ordenar por más recientes", value=True)

# ----------------- Listado -----------------
st.markdown("### 💬 COMENTARIOS DE CLIENTES")
st.markdown('<div class="list">', unsafe_allow_html=True)

filtered = [
    x for x in reviews
    if x["rating"] >= min_score and search_text.lower() in (x["comment"] or "").lower()
]
if sort_order:
    # si tu backend agrega fecha ISO, ordenar por "date"
    filtered.sort(key=lambda x: x.get("date",""), reverse=True)

if not filtered:
    st.info("No hay comentarios que coincidan con los filtros aplicados.")
else:
    for i, review in enumerate(filtered, 1):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f"**#{i} · ⭐ {review['rating']}/10**")
        st.caption(f"👤 por {review.get('user','Anónimo')} · 📅 {review.get('date','')}")
        st.write(f"_{review.get('comment','')}_")
        crit = review.get("criteria", {}) or {}
        if crit:
            st.caption("**Detalle de valoración:**")
            cols = st.columns(3)
            items = list(crit.items())
            for idx, (k, v) in enumerate(items):
                with cols[idx % 3]:
                    st.write(f"• {k.replace('_',' ').title()}: **{v}**")
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Botón volver
st.write("")
st.button("⬅️ VOLVER AL PRODUCTO", key="btn_back_ver", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)
