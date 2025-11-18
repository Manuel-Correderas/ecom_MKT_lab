# streamlit_app/pages/5_💬_Comentarios.py
import os
import json
import requests
import pandas as pd
from datetime import datetime
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="Comentarios y Valoración", layout="centered")

# ----------------- Config -----------------
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "comments.csv"
DATA_PATH.parent.mkdir(parents=True, exist_ok=True)  # asegurar carpeta data/

# Tomamos product_id de la URL (?id=...) o default 1
qp = st.query_params
PRODUCT_ID = str(qp.get("id", "1"))

# ----------------- Estilos -----------------
st.markdown("""
<style>
.stApp { background:#FF8C00; }
.panel{
  background:#f79b2f; border-radius:12px; padding:16px 18px;
  box-shadow:0 8px 18px rgba(0,0,0,.18);
}
.hdr{
  text-align:center; font-weight:900; letter-spacing:.6px;
  color:#10203a; margin-bottom:10px;
}
.row{
  background:#ffa84d; border-radius:10px; padding:6px 8px; margin:6px 0;
  box-shadow:0 1px 4px rgba(0,0,0,.12);
}
.row .lbl{ color:#1b2749; font-weight:700; }
.counter{ display:flex; gap:6px; justify-content:flex-end; align-items:center; }
.counter .score{ background:#d6d6d6; color:#000; font-weight:900; border-radius:6px; padding:3px 8px; min-width:28px; text-align:center; }
.counter button{ font-weight:900; }
.badge{ display:inline-block; background:#d6d6d6; color:#000; font-weight:900; border-radius:8px; padding:6px 10px; margin:6px 0; }
.btn-primary{ background:#0b3a91 !important; color:#fff !important; border:none !important; border-radius:8px !important; padding:10px 18px !important; font-weight:900 !important; }
.btn-secondary{ background:#936037 !important; color:#fff !important; border:none !important; border-radius:8px !important; padding:10px 18px !important; font-weight:900 !important; }
.product-header { background:#ff9b2f; padding:12px; border-radius:8px; margin-bottom:15px; }
</style>
""", unsafe_allow_html=True)

# ----------------- Cabecera -----------------
st.markdown('<div class="hdr"><h3>💬 COMENTARIOS Y VALORACIÓN</h3></div>', unsafe_allow_html=True)
st.markdown('<div class="panel">', unsafe_allow_html=True)

# (Demo) Info de producto – si querés, podés traerlo del backend /products/{id}
product_info = {
    "name": "Producto",
    "seller": "Vendedor",
    "rating": 0.0,
    "category": "-",
    "subcategory": "-"
}
st.markdown("<div class='product-header'>", unsafe_allow_html=True)
st.write(f"**📦 PRODUCTO:** {product_info['name']}  \n**ID:** {PRODUCT_ID}")
st.caption(
    f"**🏪 VENDEDOR:** {product_info['seller']} • **⭐ VALORACIÓN:** {product_info['rating']}/10  \n"
    f"**📂 CATEGORÍA:** {product_info['category']}  \n"
    f"**🔍 SUBCATEGORÍA:** {product_info['subcategory']}"
)
st.markdown("</div>", unsafe_allow_html=True)

# ----------------- Criterios -----------------
criteria = [
    ("calidad_general", "⭐ CALIDAD GENERAL"),
    ("relacion_calidad_precio", "💰 RELACIÓN CALIDAD-PRECIO"),
    ("durabilidad", "🛡️ DURABILIDAD"),
    ("descripcion_fiel", "📝 DESCRIPCIÓN FIEL"),
    ("embalaje_recepcion", "📦 EMBALAJE / ESTADO AL RECIBIR"),
    ("satisfaccion_global", "😊 SATISFACCIÓN GLOBAL"),
    ("diseno_estetica", "🎨 DISEÑO Y ESTÉTICA"),
]

# Inicializar puntuaciones (en session_state)
for key, _ in criteria:
    st.session_state.setdefault(f"rating_{key}", 9)

total_points = 0
for key, label in criteria:
    current = st.session_state[f"rating_{key}"]
    colA, colB = st.columns([3,2])
    with colA:
        st.markdown(f'<div class="row"><span class="lbl">{label}</span></div>', unsafe_allow_html=True)
    with colB:
        c1, c2, c3 = st.columns([1,1,2])
        with c1:
            if st.button("−", key=f"sub_{key}"):
                st.session_state[f"rating_{key}"] = max(1, current - 1)
                st.rerun()
        with c2:
            st.markdown(f"<div class='counter'><span class='score'>{st.session_state[f'rating_{key}']}</span></div>", unsafe_allow_html=True)
        with c3:
            if st.button("+", key=f"add_{key}"):
                st.session_state[f"rating_{key}"] = min(10, current + 1)
                st.rerun()
    total_points += st.session_state[f"rating_{key}"]

avg_score = round(total_points / len(criteria), 1)
st.markdown(f"<span class='badge'>🎯 PUNTUACIÓN FINAL: {avg_score}/10</span>", unsafe_allow_html=True)

# ----------------- Comentario libre -----------------
st.markdown("### 💭 TU COMENTARIO")
comment = st.text_area(
    "Compartí tu experiencia con este producto...",
    height=120,
    placeholder="¿Qué te pareció el producto? ¿Recomendarías la compra? ¿Algún aspecto a mejorar?",
    label_visibility="collapsed"
)

# ----------------- Guardar comentario -----------------
def save_comment(payload: dict) -> bool:
    """Intenta enviar al backend; si falla, guarda en CSV. Devuelve True si se guardó."""
    # 1) Intento backend
    try:
        r = requests.post(f"{BACKEND_URL}/comments", json=payload, timeout=8)
        if r.status_code in (200, 201):
            return True
    except Exception:
        pass
    # 2) Fallback CSV
    try:
        if DATA_PATH.exists():
            df = pd.read_csv(DATA_PATH)
        else:
            df = pd.DataFrame(columns=["product_id","user_name","rating","criteria","comment","date"])
        row = {
            "product_id": payload["product_id"],
            "user_name": payload.get("user_name", "Anónimo"),
            "rating": payload["rating"],
            "criteria": json.dumps(payload["criteria"], ensure_ascii=False),
            "comment": payload["comment"],
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        df.to_csv(DATA_PATH, index=False, encoding="utf-8")
        return True
    except Exception as e:
        st.error(f"No se pudo guardar el comentario: {e}")
        return False

col_send, col_back = st.columns(2)
with col_send:
    # 👇 Un ÚNICO botón, clave única
    if st.button("📤 ENVIAR VALORACIÓN", key="btn_send_valoracion"):
        payload = {
            "product_id": PRODUCT_ID,
            "user_name": st.session_state.get("user_name", "Anónimo"),
            "rating": float(avg_score),
            "criteria": {k: int(st.session_state[f"rating_{k}"]) for k, _ in criteria},
            "comment": comment.strip(),
        }
        if not payload["comment"]:
            st.warning("Escribí un comentario antes de enviar.")
        else:
            ok = save_comment(payload)
            if ok:
                st.success("✅ Valoración enviada correctamente.")
                st.rerun()

with col_back:
    st.button("⬅️ VOLVER", key="btn_back")

st.markdown("</div>", unsafe_allow_html=True)

# ------------- Comentarios existentes (solo ejemplo estático opcional) -------------
with st.expander("📖 COMENTARIOS EXISTENTES (ejemplo)"):
    st.markdown("""
**⭐️⭐️⭐️⭐️⭐️ María González**  
*"Excelente calidad, muy cómodo y buena terminación."*
""")
