# streamlit_app/pages/8_💰_Finanzas.py
import streamlit as st
import pandas as pd
import requests
from datetime import date, timedelta

st.set_page_config(page_title="Finanzas y Rentabilidad", page_icon="💰", layout="wide")

# =======================
# BACKEND_URL (robusto sin secrets.toml)
# =======================
try:
    BACKEND_URL = st.secrets["BACKEND_URL"]
except Exception:
    BACKEND_URL = "http://localhost:8000"  # fallback local
    # Si querés ver esto en la UI, descomentá:
    # st.info("Usando BACKEND_URL por defecto: http://localhost:8000")

# =======================
# HEADER
# =======================
st.title("Finanzas y Rentabilidad")
st.caption("Dashboard financiero del vendedor con datos reales del backend.")

# =======================
# SIDEBAR – FILTROS
# =======================
st.sidebar.header("Filtros")

hoy = date.today()
inicio = hoy - timedelta(days=30)
rangos = st.sidebar.date_input("Rango de fechas", (inicio, hoy), format="DD/MM/YYYY")

moneda = st.sidebar.selectbox("Moneda", ["ARS", "USD"], index=0)
canales = st.sidebar.multiselect(
    "Canales",
    ["tienda", "marketplace", "instagram", "whatsapp"],
    default=["tienda"]
)

mostrar_iva = st.sidebar.toggle("Mostrar IVA (21%)", value=False)
top_n = st.sidebar.slider("Top productos", 3, 15, 8)

params = {
    "start": str(rangos[0]),
    "end": str(rangos[1]),
    "currency": moneda,
    "channels": ",".join(canales)
}

# =======================
# HELPERS
# =======================
def api_get(path: str):
    try:
        res = requests.get(f"{BACKEND_URL}{path}", params=params, timeout=10)
        if res.status_code == 200:
            return res.json()
        st.error(f"Error {res.status_code}: {res.text}")
        return None
    except Exception as e:
        st.error(f"No se pudo conectar al backend: {e}")
        return None

# =======================
# 1) KPIs
# =======================
st.subheader("📊 KPIs Financieros")

summary = api_get("/analytics/sales-summary") or {
    "total_sales": 0,
    "total_margin": 0,
    "ticket_avg": 0,
    "returns": 0
}

ventas = summary["total_sales"]
margen = summary["total_margin"]
ticket = summary["ticket_avg"]
devoluciones = summary["returns"]

if mostrar_iva:
    ventas *= 1.21
    margen *= 1.21

c1, c2, c3, c4 = st.columns(4)
c1.metric("Ventas", f"$ {ventas:,.0f}".replace(",", "."))
c2.metric(
    "Margen",
    f"$ {margen:,.0f}".replace(",", "."),
    delta=f"{(margen / ventas * 100) if ventas else 0:.1f}%"
)
c3.metric("Ticket Promedio", f"$ {ticket:,.0f}".replace(",", "."))
c4.metric("Devoluciones", devoluciones)

st.divider()

# =======================
# 2) Gráfico – ventas diarias
# =======================
st.subheader("📈 Evolución diaria de ventas")

daily = api_get("/analytics/sales-daily")

if daily:
    df_daily = pd.DataFrame(daily)
    st.line_chart(df_daily, x="date", y="total")
else:
    st.info("No hay datos de ventas en este período.")

col1, col2 = st.columns(2)

# =======================
# 3) Margen por categoría
# =======================
with col1:
    st.subheader("📦 Margen por categoría")
    margins = api_get("/analytics/category-margins")
    if margins:
        df_margins = pd.DataFrame(margins)
        st.bar_chart(df_margins, x="category", y="margin")
    else:
        st.info("No hay datos para mostrar.")

# =======================
# 4) Top productos
# =======================
with col2:
    st.subheader("🏆 Top productos por ventas")
    params["top"] = top_n  # agregamos top al query
    top = api_get("/analytics/top-products")
    if top:
        df_top = pd.DataFrame(top)
        st.bar_chart(df_top, x="product", y="sales")
    else:
        st.info("Sin productos para mostrar.")

st.divider()

# =======================
# 5) Detalle de operaciones
# =======================
st.subheader("🧾 Detalle de operaciones")
ops = api_get("/analytics/operations")

if ops:
    df_ops = pd.DataFrame(ops)
    st.dataframe(df_ops, use_container_width=True)
else:
    st.info("No existen operaciones registradas en el período seleccionado.")
