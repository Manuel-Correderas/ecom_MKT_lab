# streamlit_app/pages/0a_📊_Dashboard_Global.py
import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta, date

# ========================================
# CONFIG
# ========================================
st.set_page_config(page_title="Dashboard Global - MKT", layout="wide")
st.title("Dashboard Global")
st.caption("Resumen general de actividad, ventas y rendimiento.")

try:
    BACKEND_URL = st.secrets["BACKEND_URL"]
except Exception:
    BACKEND_URL = "http://localhost:8000"

# ========================================
# HELPERS API
# ========================================

def get_auth_headers():
    token = st.session_state.get("auth_token")
    return {"Authorization": f"Bearer {token}"} if token else {}

def api_get_global_metrics():
    try:
        r = requests.get(f"{BACKEND_URL}/analytics/global", headers=get_auth_headers(), timeout=10)
        return r.json() if r.status_code == 200 else None
    except:
        return None

def api_get_orders(from_date: date, to_date: date):
    try:
        params = {
            "from": from_date.isoformat(),
            "to": to_date.isoformat()
        }
        r = requests.get(f"{BACKEND_URL}/analytics/orders", params=params, headers=get_auth_headers(), timeout=15)
        if r.status_code == 200:
            return r.json()
        return []
    except:
        return []

# ========================================
# FILTROS LATERALES
# ========================================
st.sidebar.header("Filtros")

hoy = date.today()
desde = st.sidebar.date_input("Desde", hoy - timedelta(days=30))
hasta = st.sidebar.date_input("Hasta", hoy)

if isinstance(desde, list):  # Streamlit bug fix
    desde = desde[0]
if isinstance(hasta, list):
    hasta = hasta[0]

# ========================================
# TRAER DATOS DEL BACKEND
# ========================================

global_data = api_get_global_metrics() or {}
orders_data = api_get_orders(desde, hasta)

# Convertir órdenes a DataFrame seguro
if orders_data:
    df_orders = pd.DataFrame(orders_data)
else:
    df_orders = pd.DataFrame(columns=["order_date", "seller_name", "product_name", "qty", "total_paid", "payment_method", "status"])

# Normalizar campos esperados
if "order_date" in df_orders:
    df_orders["order_date"] = pd.to_datetime(df_orders["order_date"])
else:
    df_orders["order_date"] = pd.to_datetime([])

df_orders["qty"] = df_orders.get("qty", 1)
df_orders["total_paid"] = df_orders.get("total_paid", 0)

# ========================================
# KPIs
# ========================================

total_users = global_data.get("total_users", 0)
total_products = global_data.get("total_products", 0)

gmv = float(df_orders["total_paid"].sum()) if not df_orders.empty else 0.0
orders_count = len(df_orders)
aov = gmv / orders_count if orders_count else 0.0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Usuarios totales", f"{total_users:,}".replace(",", "."))
c2.metric("Productos publicados", f"{total_products:,}".replace(",", "."))
c3.metric("GMV (ventas cobradas)", f"$ {int(gmv):,}".replace(",", "."))
c4.metric("Ticket medio (AOV)", f"$ {int(aov):,}".replace(",", "."))

st.divider()

# ========================================
# EVOLUCIÓN DE VENTAS
# ========================================
st.subheader("Evolución de ventas")

if not df_orders.empty:
    df_orders["day"] = df_orders["order_date"].dt.floor("D")
    daily = df_orders.groupby("day", as_index=False).agg(
        gmv=("total_paid", "sum"),
        orders=("order_date", "count")
    )

    chart_df = daily.set_index("day")[["gmv", "orders"]]
    st.line_chart(chart_df, height=260)
else:
    st.info("Sin datos en el rango seleccionado.")

# ========================================
# RANKINGS
# ========================================

colA, colB = st.columns(2)

with colA:
    st.subheader("Top vendedores por GMV")
    if not df_orders.empty:
        df_sellers = df_orders.groupby("seller_name", as_index=False)["total_paid"].sum()
        df_sellers = df_sellers.sort_values("total_paid", ascending=False).head(10)
        st.bar_chart(df_sellers.set_index("seller_name")["total_paid"], height=260)
    else:
        st.info("Sin datos de órdenes.")

with colB:
    st.subheader("Top productos por unidades")
    if not df_orders.empty:
        df_products = df_orders.groupby("product_name", as_index=False)["qty"].sum()
        df_products = df_products.sort_values("qty", ascending=False).head(10)
        st.bar_chart(df_products.set_index("product_name")["qty"], height=260)
    else:
        st.info("Sin datos de órdenes.")

st.divider()

# ========================================
# CATÁLOGO Y PAGOS
# ========================================

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Catálogo")
    st.write(f"• Sin stock: **{global_data.get('products_out_of_stock', 0)}**")
    st.write(f"• Con imagen: **{global_data.get('products_with_image', 0)}**")
    st.write("• Top categorías:")
    top_cat = global_data.get("top_categories", ["Indumentaria", "Electrónica", "Accesorios"])
    st.write(pd.Series(top_cat))

with col2:
    st.subheader("Métodos de pago")
    if not df_orders.empty and "payment_method" in df_orders:
        st.bar_chart(df_orders["payment_method"].value_counts(), height=260)
    else:
        st.info("Sin datos de pagos.")

with col3:
    st.subheader("Calidad de órdenes")
    if not df_orders.empty and "status" in df_orders:
        fail_rate = (df_orders["status"].str.lower() == "failed").mean() * 100
        st.metric("Tasa de fallos de pago", f"{fail_rate:.1f}%")
    else:
        st.info("Sin estados de orden.")

st.divider()

# ========================================
# MONETIZACIÓN (Estático)
# ========================================
st.subheader("Monetización & Premium")
m1, m2 = st.columns([2, 1])
with m1:
    st.write("Accedé a planes Premium para mejorar la visibilidad y reducir comisiones.")
with m2:
    st.button("Ver planes Premium", type="primary")

st.caption("Panel conectado al backend — datos reales desde FastAPI.")
