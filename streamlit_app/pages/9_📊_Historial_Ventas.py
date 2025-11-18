# streamlit_app/pages/9_📈_Historial_Ventas.py
import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta, date

st.set_page_config(page_title="Historial de Ventas (Vendedor)", layout="centered")

# --- FIX sin secrets.toml ---
try:
    BACKEND_URL = st.secrets["BACKEND_URL"]
except Exception:
    BACKEND_URL = "http://localhost:8000"


# =============== Estilos ===============
st.markdown("""
<style>
.stApp { background:#FF8C00; }
.panel { 
    background:#f79b2f; 
    border-radius:14px; 
    padding:16px 18px;
    box-shadow:0 8px 18px rgba(0,0,0,.18); 
}
.hdr { 
    text-align:center; 
    font-weight:900; 
    letter-spacing:.6px;
    color:#10203a; 
    margin-bottom:12px; 
}
.sub { 
    color:#162c56; 
    font-size:.92rem; 
}
.list { 
    background:#ffa84d; 
    border-radius:10px; 
    padding:10px; 
    margin-top:8px;
    max-height: 460px; 
    overflow-y: auto; 
    box-shadow: inset 0 1px 4px rgba(0,0,0,.12); 
}
.card { 
    background:#fff5e6; 
    border-radius:10px; 
    padding:12px;
    box-shadow:0 2px 8px rgba(0,0,0,.12); 
    margin-bottom:10px; 
}
.badge { 
    display:inline-block; 
    background:#d6d6d6; 
    color:#000; 
    font-weight:900;
    border-radius:8px; 
    padding:6px 10px; 
    margin:6px 0; 
}
.small { 
    font-size:.86rem; 
    color:#333; 
}
.btn-primary { 
    background:#0b3a91 !important; 
    color:#fff !important; 
    border:none !important; 
    border-radius:8px !important;
    padding:8px 14px !important; 
    font-weight:900 !important;
}
.btn-secondary { 
    background:#936037 !important; 
    color:#fff !important; 
    border:none !important; 
    border-radius:8px !important;
    padding:8px 14px !important; 
    font-weight:900 !important;
}
.seller-header {
    background:#ff9b2f;
    padding:12px;
    border-radius:8px;
    margin-bottom:15px;
    text-align:center;
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


# =============== Helper API ===============
def api_get_sales_history(start: date, end: date, status: str, search: str):
    """Llama al backend /sales/history con filtros."""
    params = {
        "start": start.isoformat(),
        "end": end.isoformat(),
    }
    if status and status != "Todos":
        # mapeamos estados visuales -> códigos backend
        mapping = {
            "Entregados": "DELIVERED",
            "En camino": "SHIPPED",
            "Pendientes": "PENDING",
        }
        params["status"] = mapping.get(status, status)
    if search:
        params["search"] = search

    try:
        r = requests.get(f"{BACKEND_URL}/sales/history", params=params, timeout=10)
        if r.status_code == 200:
            return r.json()
        st.error(f"Error al obtener ventas ({r.status_code}): {r.text}")
        return []
    except Exception as e:
        st.error(f"No se pudo conectar al backend: {e}")
        return []


# =============== Encabezado ===============
st.markdown('<div class="hdr"><h3>📈 HISTORIAL DE VENTAS</h3></div>', unsafe_allow_html=True)
st.markdown('<div class="panel">', unsafe_allow_html=True)

# Información básica del vendedor (puede venir del session_state)
seller_name = st.session_state.get("seller_alias", "H&M")
st.markdown("<div class='seller-header'>", unsafe_allow_html=True)
st.markdown(f"### 🏪 {seller_name} - VENDEDOR")
st.markdown("**📊 RESUMEN DE VENTAS (según filtros seleccionados)**")
st.markdown("</div>", unsafe_allow_html=True)

# =============== Filtros ===============
st.markdown("### 🔍 BUSCAR VENTAS")

col_search, col_filter1, col_filter2 = st.columns([2, 1, 1])
with col_search:
    search_query = st.text_input("", placeholder="Buscar por producto, cliente, factura...")
with col_filter1:
    date_filter = st.selectbox("Fecha", ["Últimos 7 días", "Este mes", "Últimos 3 meses", "Todo"])
with col_filter2:
    status_filter = st.selectbox("Estado", ["Todos", "Entregados", "En camino", "Pendientes"])

hoy = date.today()
if date_filter == "Últimos 7 días":
    start_date = hoy - timedelta(days=7)
elif date_filter == "Este mes":
    start_date = hoy.replace(day=1)
elif date_filter == "Últimos 3 meses":
    # aprox 90 días
    start_date = hoy - timedelta(days=90)
else:
    # "Todo": un año para atrás por defecto
    start_date = hoy - timedelta(days=365)

end_date = hoy

# =============== Traer datos del backend ===============
sales_data = api_get_sales_history(start_date, end_date, status_filter, search_query)

# Normalizar en DataFrame
df_sales = pd.DataFrame(sales_data) if sales_data else pd.DataFrame()

# Esperamos algo así desde el backend para cada venta:
# {
#   "id": "V-001",
#   "product_name": "...",
#   "category": "...",
#   "subcategory": "...",
#   "date": "2024-03-15T14:30:00",
#   "client_name": "...",
#   "client_address": "...",
#   "quantity": 1,
#   "unit_price": 25999,
#   "total": 25999,
#   "invoice": "FAC-2024-001",
#   "status": "DELIVERED",
#   "product_rating": 9.5,
#   "client_rating": 10,
#   "stock_at_sale": 15
# }

# Si hay fecha en ISO, separamos fecha y hora para mostrar lindo
if not df_sales.empty and "date" in df_sales.columns:
    try:
        dt_series = pd.to_datetime(df_sales["date"])
        df_sales["date_str"] = dt_series.dt.strftime("%d/%m/%Y")
        df_sales["time_str"] = dt_series.dt.strftime("%H:%M")
    except Exception:
        df_sales["date_str"] = df_sales["date"].astype(str)
        df_sales["time_str"] = ""

# =============== Resumen automático ===============
if df_sales.empty:
    total_ventas = 0
    ingresos_totales = 0
    valoracion_prom = 0
    clientes_satisfechos = 0
else:
    total_ventas = len(df_sales)
    ingresos_totales = float(df_sales.get("total", 0).sum())
    # Rating de producto
    if "product_rating" in df_sales.columns:
        # ignoramos None / NaN
        valoracion_prom = float(
            df_sales["product_rating"].dropna().astype(float).mean()
        ) if df_sales["product_rating"].notna().any() else 0
    else:
        valoracion_prom = 0

    # % clientes satisfechos (cliente_rating >= 8)
    if "client_rating" in df_sales.columns:
        cr = df_sales["client_rating"].dropna()
        if len(cr) > 0:
            clientes_satisfechos = float((cr.astype(float) >= 8).mean() * 100)
        else:
            clientes_satisfechos = 0
    else:
        clientes_satisfechos = 0

st.markdown(
    f"**📊 RESUMEN:** {total_ventas} VENTAS • "
    f"⭐ {valoracion_prom:.1f}/10 VALORACIÓN PROMEDIO • "
    f"${ingresos_totales:,.0f} INGRESOS TOTALES".replace(",", ".")
)

# =============== Lista de Ventas ===============
st.markdown('<div class="list">', unsafe_allow_html=True)

if df_sales.empty:
    st.info("No se encontraron ventas que coincidan con los filtros o no hay datos aún.")
else:
    # iterar sobre ventas
    for _, sale in df_sales.iterrows():
        sale_id = str(sale.get("id", ""))
        product_name = sale.get("product_name", "Producto sin nombre")
        category = sale.get("category", "Sin categoría")
        subcategory = sale.get("subcategory", "Sin subcategoría")
        date_str = sale.get("date_str", sale.get("date", ""))
        time_str = sale.get("time_str", "")
        client_name = sale.get("client_name", "Cliente")
        client_address = sale.get("client_address", "-")
        quantity = int(sale.get("quantity", 0))
        unit_price = float(sale.get("unit_price", 0))
        total = float(sale.get("total", quantity * unit_price))
        invoice = sale.get("invoice", "-")
        status_backend = str(sale.get("status", ""))

        # mapear status backend -> label visual
        status_map = {
            "DELIVERED": "Entregado",
            "SHIPPED": "En camino",
            "PENDING": "Pendiente",
        }
        status_label = status_map.get(status_backend, status_backend or "Desconocido")

        # color emoji
        if status_label == "Entregado":
            status_color = "🟢"
        elif status_label == "En camino":
            status_color = "🟡"
        else:
            status_color = "🔴"

        product_rating = sale.get("product_rating", "-")
        client_rating_raw = sale.get("client_rating", "-")
        stock_at_sale = sale.get("stock_at_sale", "-")

        st.markdown('<div class="card">', unsafe_allow_html=True)

        # Header de la venta
        col_header1, col_header2 = st.columns([4, 1])
        with col_header1:
            st.markdown(f"**🛍️ {product_name}**")
            st.caption(f"📂 {category} • 🔍 {subcategory}")
        with col_header2:
            st.markdown(f"**{status_color} {status_label}**")

        # Detalles de la venta
        col_details1, col_details2 = st.columns(2)
        with col_details1:
            st.markdown(
                f"**📅 Fecha:** {date_str} {time_str}  \n"
                f"**👤 Cliente:** {client_name}  \n"
                f"**🏠 Dirección:** {client_address}  \n"
                f"**📦 Cantidad:** {quantity}  \n"
                f"**💰 Precio Unitario:** ${unit_price:,.0f}".replace(",", ".")
            )
        with col_details2:
            st.markdown(
                f"**🧾 Factura:** {invoice}  \n"
                f"**📊 Stock al momento:** {stock_at_sale}  \n"
                f"**⭐ Valoración Producto:** {product_rating if product_rating != '-' else '-'}"
                f"{'/10' if product_rating not in (None, '-') else ''}  \n"
                f"**😊 Valoración Cliente:** {client_rating_raw if client_rating_raw != '-' else '-'}"
                f"{'/10' if client_rating_raw not in (None, '-') else ''}  \n"
                f"**🎯 Estado:** {status_label}"
            )

        # Total y acciones
        st.markdown(
            f"<span class='badge'>💵 TOTAL VENTA: ${total:,.0f}</span>".replace(",", "."),
            unsafe_allow_html=True
        )

        # Sección de gestión
        st.markdown("### 🛠️ GESTIÓN DE VENTA")
        col_manage1, col_manage2, col_manage3 = st.columns(3)
        
        # Valoración cliente editable (solo front, el PUT al backend lo podés agregar después)
        with col_manage1:
            st.markdown("**📊 Valorar Cliente**")
            # valor por defecto: rating actual o 5
            try:
                default_rating = int(client_rating_raw) if client_rating_raw not in (None, "-", "") else 5
            except Exception:
                default_rating = 5
            client_rating = st.slider(
                "Puntuación del cliente",
                1, 10,
                value=default_rating,
                key=f"rate_{sale_id}"
            )
        
        with col_manage2:
            st.markdown("**📎 Comprobante**")
            st.file_uploader(
                "Subir archivo", 
                type=["pdf", "png", "jpg"],
                key=f"file_{sale_id}", 
                label_visibility="collapsed"
            )
        
        with col_manage3:
            st.markdown("**⚡ Acciones**")
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                st.button("💾 GUARDAR", key=f"save_{sale_id}", use_container_width=True)
            with col_btn2:
                st.button("📧 CONTACTAR", key=f"contact_{sale_id}", use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # /list

# =============== Pie ===============
st.write("")
col_back = st.columns([1])[0]
with col_back:
    st.button("⬅️ VOLVER AL PANEL", key="btn_back", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)  # /panel

# Resumen estadístico (con datos reales)
with st.expander("📊 ESTADÍSTICAS DETALLADAS"):
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    with col_stat1:
        st.metric("Ventas Totales", f"{total_ventas}")
    with col_stat2:
        st.metric("Ingresos Totales", f"${ingresos_totales:,.0f}".replace(",", "."))
    with col_stat3:
        st.metric("Valoración Promedio", f"{valoracion_prom:.1f}/10")
    with col_stat4:
        st.metric("Clientes Satisfechos", f"{clientes_satisfechos:.0f}%")

    if not df_sales.empty and "category" in df_sales.columns:
        st.markdown("**📈 Distribución por Categoría:**")
        dist = df_sales.groupby("category")["total"].sum().sort_values(ascending=False)
        for cat, monto in dist.items():
            st.markdown(f"- {cat}: ${monto:,.0f}".replace(",", "."))
    else:
        st.markdown("No hay datos suficientes para mostrar distribución por categoría.")
