# streamlit_app/pages/8_📊_Dashboard_Local.py
import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Dashboard Local", layout="wide")

# =======================
# CONFIG / BACKEND
# =======================
try:
    BACKEND_URL = st.secrets["BACKEND_URL"]
except Exception:
    BACKEND_URL = "http://localhost:8000"

def get_auth_headers():
    token = st.session_state.get("auth_token")
    return {"Authorization": f"Bearer {token}"} if token else {}

def api_get_local_dashboard(role: str):
    """
    Pide el dashboard local al backend según el rol.
    Espera algo como:
      - /analytics/seller/dashboard  para VENDEDOR
      - /analytics/buyer/dashboard   para COMPRADOR
    """
    try:
        if role == "VENDEDOR":
            endpoint = f"{BACKEND_URL}/analytics/seller/dashboard"
        else:
            endpoint = f"{BACKEND_URL}/analytics/buyer/dashboard"

        r = requests.get(endpoint, headers=get_auth_headers(), timeout=10)
        if r.status_code == 200:
            return r.json()
        return {}
    except Exception:
        return {}


# =======================
# Estilos
# =======================
st.markdown("""
<style>
.stApp { background:#FF8C00; }
.dashboard-panel {
    background:#f79b2f; 
    border-radius:12px; 
    padding:20px; 
    margin-bottom:20px;
    box-shadow:0 8px 18px rgba(0,0,0,.18);
}
.metric-card {
    background:#fff5e6;
    border-radius:10px;
    padding:15px;
    text-align:center;
    box-shadow:0 2px 8px rgba(0,0,0,.12);
}
.section-title {
    color:#1f2e5e;
    font-weight:800;
    margin:20px 0 10px 0;
    border-bottom:2px solid #0b3a91;
    padding-bottom:5px;
}
</style>
""", unsafe_allow_html=True)

# =======================
# Encabezado
# =======================
st.markdown('<div class="dashboard-panel">', unsafe_allow_html=True)
st.markdown("## 📊 DASHBOARD LOCAL")
st.markdown("**Panel de control y métricas de tu actividad**")
st.markdown('</div>', unsafe_allow_html=True)

# =======================
# Selector de Vista (según rol)
# =======================
role = st.session_state.get("user_role", "VENDEDOR")  # 'VENDEDOR' / 'COMPRADOR'
options = ["Vendedor", "Comprador"]

default_idx = 0
if role == "COMPRADOR":
    default_idx = 1

st.markdown('<div class="dashboard-panel">', unsafe_allow_html=True)
view_mode = st.radio(
    "**👤 VER COMO:**",
    options,
    horizontal=True,
    key="view_mode",
    index=default_idx
)
st.markdown('</div>', unsafe_allow_html=True)

# Traducir a "rol" del backend
role_for_backend = "VENDEDOR" if view_mode == "Vendedor" else "COMPRADOR"

# =======================
# Traer datos del backend
# =======================
data = api_get_local_dashboard(role_for_backend)

# Estructura esperada (pero todo con fallback por si no existe)
kpis = data.get("kpis", {})
series = data.get("series", {})
lists = data.get("lists", {})

# =======================
# KPIs Principales
# =======================
st.markdown('<div class="dashboard-panel">', unsafe_allow_html=True)
st.markdown("### 📈 MÉTRICAS PRINCIPALES")

if view_mode == "Vendedor":
    ventas_totales = kpis.get("total_sales", 248950)
    pedidos = kpis.get("orders_count", 156)
    rating = kpis.get("rating", 9.2)
    devoluciones = kpis.get("returns", 4)
    delta_sales = kpis.get("sales_delta_label", "+12% vs mes anterior")
    delta_orders = kpis.get("orders_delta_label", "+8% vs mes anterior")
    delta_rating = kpis.get("rating_delta_label", "+0.3 puntos")
    delta_returns = kpis.get("returns_delta_label", "-2% vs mes anterior")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("💰 VENTAS TOTALES", f"$ {ventas_totales:,.0f}".replace(",", "."), delta_sales)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("📦 PEDIDOS", f"{pedidos}", delta_orders)
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("⭐ VALORACIÓN", f"{rating:.1f}/10", delta_rating)
        st.markdown('</div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("🔄 DEVOLUCIONES", f"{devoluciones}", delta_returns)
        st.markdown('</div>', unsafe_allow_html=True)
else:
    total_spent = kpis.get("total_spent", 45850)
    orders = kpis.get("orders_count", 12)
    avg_rating = kpis.get("avg_rating", 9.5)
    fav_products = kpis.get("fav_products_count", 8)
    delta_spent = kpis.get("spent_delta_label", "+15% vs mes anterior")
    delta_orders = kpis.get("orders_delta_label", "+2 vs mes anterior")
    delta_rating = kpis.get("rating_delta_label", "+0.2 puntos")
    delta_favs = kpis.get("fav_delta_label", "+3 vs mes anterior")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("🛍️ COMPRAS TOTALES", f"$ {total_spent:,.0f}".replace(",", "."), delta_spent)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("📦 PEDIDOS", f"{orders}", delta_orders)
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("⭐ VALORACIÓN PROMEDIO", f"{avg_rating:.1f}/10", delta_rating)
        st.markdown('</div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("🎯 PRODUCTOS FAVORITOS", f"{fav_products}", delta_favs)
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# =======================
# Gráficos y Evolución
# =======================
st.markdown('<div class="dashboard-panel">', unsafe_allow_html=True)
st.markdown("### 📊 EVOLUCIÓN TEMPORAL")

col_chart1, col_chart2 = st.columns(2)

if view_mode == "Vendedor":
    # Ventas mensuales
    with col_chart1:
        st.markdown("**📈 Ventas Mensuales**")
        ventas_mensuales = series.get("monthly_sales", [])
        if ventas_mensuales:
            df = pd.DataFrame(ventas_mensuales)  # espera columns: ["period", "total"]
            if "period" in df.columns and "total" in df.columns:
                df = df.set_index("period")
                st.line_chart(df["total"], height=260)
            else:
                st.info("Formato de 'monthly_sales' no válido.")
        else:
            st.markdown(
                '<div style="background:#fff5e6; border-radius:8px; padding:80px 20px; text-align:center; border:1px solid #ddd;">'
                '<span style="color:#666;">Gráfico de Ventas Mensuales (sin datos)</span>'
                '</div>', 
                unsafe_allow_html=True
            )

    # Pedidos por categoría
    with col_chart2:
        st.markdown("**📦 Pedidos por Categoría**")
        pedidos_cat = series.get("orders_by_category", [])
        if pedidos_cat:
            df = pd.DataFrame(pedidos_cat)  # espera ["category", "orders"]
            if "category" in df.columns and "orders" in df.columns:
                st.bar_chart(df.set_index("category")["orders"], height=260)
            else:
                st.info("Formato de 'orders_by_category' no válido.")
        else:
            st.markdown(
                '<div style="background:#fff5e6; border-radius:8px; padding:80px 20px; text-align:center; border:1px solid #ddd;">'
                '<span style="color:#666;">Gráfico de Pedidos por Categoría (sin datos)</span>'
                '</div>', 
                unsafe_allow_html=True
            )
else:
    # Compras mensuales
    with col_chart1:
        st.markdown("**🛍️ Compras Mensuales**")
        compras_mensuales = series.get("monthly_purchases", [])
        if compras_mensuales:
            df = pd.DataFrame(compras_mensuales)  # ["period", "amount"]
            if "period" in df.columns and "amount" in df.columns:
                df = df.set_index("period")
                st.line_chart(df["amount"], height=260)
            else:
                st.info("Formato de 'monthly_purchases' no válido.")
        else:
            st.markdown(
                '<div style="background:#fff5e6; border-radius:8px; padding:80px 20px; text-align:center; border:1px solid #ddd;">'
                '<span style="color:#666;">Gráfico de Compras Mensuales (sin datos)</span>'
                '</div>', 
                unsafe_allow_html=True
            )

    # Valoraciones por producto
    with col_chart2:
        st.markdown("**⭐ Valoraciones por Producto**")
        ratings_prod = series.get("ratings_by_product", [])
        if ratings_prod:
            df = pd.DataFrame(ratings_prod)  # ["product_name", "rating"]
            if "product_name" in df.columns and "rating" in df.columns:
                st.bar_chart(df.set_index("product_name")["rating"], height=260)
            else:
                st.info("Formato de 'ratings_by_product' no válido.")
        else:
            st.markdown(
                '<div style="background:#fff5e6; border-radius:8px; padding:80px 20px; text-align:center; border:1px solid #ddd;">'
                '<span style="color:#666;">Gráfico de Valoraciones (sin datos)</span>'
                '</div>', 
                unsafe_allow_html=True
            )

st.markdown('</div>', unsafe_allow_html=True)

# =======================
# Top Productos / Marcas
# =======================
st.markdown('<div class="dashboard-panel">', unsafe_allow_html=True)

if view_mode == "Vendedor":
    st.markdown("### 🏆 TOP PRODUCTOS MÁS VENDIDOS")
    top_products = lists.get("top_products", [
        {"name": "Jean Slim Azul", "price": 25999, "sold": 45, "rating": 9.2},
        {"name": "Remera Básica Negra", "price": 8999, "sold": 32, "rating": 8.7},
        {"name": "Zapatillas Urbanas", "price": 45999, "sold": 18, "rating": 9.5},
    ])

    col_top1, col_top2, col_top3 = st.columns(3)
    cols = [col_top1, col_top2, col_top3]
    for idx, product in enumerate(top_products[:3]):
        with cols[idx]:
            st.markdown(f"**🥇🥈🥉"[idx] + f" {product.get('name', 'Producto')}**")
            st.markdown(f"💰 ${int(product.get('price', 0)):,} c/u".replace(",", "."))
            st.markdown(f"📦 {product.get('sold', 0)} vendidos")
            st.markdown(f"⭐ {float(product.get('rating', 0)):.1f}/10")
else:
    st.markdown("### 🏆 TUS MARCAS FAVORITAS")
    top_brands = lists.get("top_brands", [
        {"name": "H&M", "orders": 8, "spent": 28950, "rating": 9.2},
        {"name": "SportShop", "orders": 3, "spent": 12500, "rating": 9.5},
        {"name": "TechStore", "orders": 1, "spent": 4400, "rating": 9.0},
    ])

    col_top1, col_top2, col_top3 = st.columns(3)
    cols = [col_top1, col_top2, col_top3]
    for idx, brand in enumerate(top_brands[:3]):
        with cols[idx]:
            st.markdown(f"**🥇🥈🥉"[idx] + f" {brand.get('name', 'Marca')}**")
            st.markdown(f"🛍️ {brand.get('orders', 0)} compras")
            st.markdown(f"💰 ${int(brand.get('spent', 0)):,} gastado".replace(",", "."))
            st.markdown(f"⭐ {float(brand.get('rating', 0)):.1f}/10")

st.markdown('</div>', unsafe_allow_html=True)

# =======================
# Actividad Reciente
# =======================
st.markdown('<div class="dashboard-panel">', unsafe_allow_html=True)
st.markdown("### 📋 ACTIVIDAD RECIENTE")

if view_mode == "Vendedor":
    recent_orders = lists.get("recent_orders", [])
    if not recent_orders:
        # fallback a lo que ya tenías
        st.markdown("**Últimos Pedidos:**")
        st.markdown("- 🟢 **Pedido #001** - Jean Slim Azul - $25,999 - Cliente: María G.")
        st.markdown("- 🟢 **Pedido #002** - Remera Negra (x2) - $17,998 - Cliente: Carlos R.")
        st.markdown("- 🟡 **Pedido #003** - Zapatillas Urbanas - $45,999 - Cliente: Laura M. (En camino)")
        st.markdown("- 🔴 **Pedido #004** - Auriculares - $14,999 - Cliente: Ana L. (Pendiente)")
    else:
        st.markdown("**Últimos Pedidos:**")
        for o in recent_orders:
            status_icon = {
                "ENTREGADO": "🟢",
                "EN_CAMINO": "🟡",
                "PENDIENTE": "🔴"
            }.get(str(o.get("status", "")).upper(), "🔘")
            st.markdown(
                f"- {status_icon} **Pedido #{o.get('code', o.get('id', ''))}** - "
                f"{o.get('product_name', '')} - "
                f"${int(o.get('total', 0)):,} - "
                f"Cliente: {o.get('client_name', '-')}".replace(",", ".")
            )
else:
    recent_purchases = lists.get("recent_purchases", [])
    if not recent_purchases:
        st.markdown("**Tus Últimas Compras:**")
        st.markdown("- 🟢 **Compra #001** - Jean Slim Azul - $25,999 - Entregado")
        st.markdown("- 🟢 **Compra #002** - Remera Negra (x2) - $17,998 - Entregado")
        st.markdown("- 🟡 **Compra #003** - Zapatillas Urbanas - $45,999 - En camino")
        st.markdown("- ⭐ **Valoración:** Dejaste 5 estrellas para Jean Slim Azul")
    else:
        st.markdown("**Tus Últimas Compras:**")
        for c in recent_purchases:
            status_icon = {
                "ENTREGADO": "🟢",
                "EN_CAMINO": "🟡",
                "PENDIENTE": "🔴"
            }.get(str(c.get("status", "")).upper(), "🔘")
            st.markdown(
                f"- {status_icon} **Compra #{c.get('code', c.get('id', ''))}** - "
                f"{c.get('product_name', '')} - "
                f"${int(c.get('total', 0)):,} - "
                f"{c.get('status_label', 'Estado no disponible')}".replace(",", ".")
            )

st.markdown('</div>', unsafe_allow_html=True)

# =======================
# Acciones Rápidas
# =======================
st.markdown('<div class="dashboard-panel">', unsafe_allow_html=True)
st.markdown("### ⚡ ACCIONES RÁPIDAS")

if view_mode == "Vendedor":
    col_action1, col_action2, col_action3 = st.columns(3)
    with col_action1:
        st.button("📦 GESTIONAR PEDIDOS", use_container_width=True)
    with col_action2:
        st.button("📊 VER REPORTES", use_container_width=True)
    with col_action3:
        st.button("🔄 ACTUALIZAR STOCK", use_container_width=True)
else:
    col_action1, col_action2, col_action3 = st.columns(3)
    with col_action1:
        st.button("🛍️ SEGUIR COMPRANDO", use_container_width=True)
    with col_action2:
        st.button("⭐ DEJAR VALORACIONES", use_container_width=True)
    with col_action3:
        st.button("📋 VER HISTORIAL", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)
