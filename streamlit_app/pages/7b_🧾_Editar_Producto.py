# streamlit_app/pages/7b_✏️_Editar_Producto.py
import os
import requests
import streamlit as st

st.set_page_config(page_title="Editar Producto (Vendedor)", layout="centered")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# ===== Helpers backend =====
def get_product_id() -> str | None:
    """Intenta obtener el ID de producto desde query params o session."""
    qp = st.query_params
    pid = qp.get("product_id")
    if not pid:
        pid = st.session_state.get("edit_product_id")
    return pid

def fetch_product(product_id: str):
    try:
        r = requests.get(f"{BACKEND_URL}/products/{product_id}", timeout=10)
        if r.status_code == 200:
            return r.json()
        st.error(f"No se pudo cargar el producto (HTTP {r.status_code}).")
    except requests.RequestException:
        st.error("No se pudo conectar al backend para cargar el producto.")
    return None

def update_product(product_id: str, payload: dict):
    try:
        r = requests.put(f"{BACKEND_URL}/products/{product_id}", json=payload, timeout=10)
        if r.status_code == 200:
            st.success("✅ Cambios guardados correctamente.")
            # Podés redirigir de vuelta a Mis Productos si querés:
            # st.switch_page("pages/7_📦_Mis_Productos.py")
        else:
            st.error(f"Error al guardar (HTTP {r.status_code}).")
    except requests.RequestException:
        st.error("No se pudo conectar al backend para guardar los cambios.")

# ===== Estilos =====
st.markdown("""
<style>
.stApp { background:#FF8C00; }
.panel{
  background:#f79b2f; border-radius:18px; padding:18px;
  box-shadow:0 8px 18px rgba(0,0,0,.18);
}
.hdr{ 
    text-align:center; 
    font-weight:900; 
    letter-spacing:.6px; 
    color:#10203a; 
    margin-bottom:10px; 
}
.btn-primary { 
    background:#0b3a91 !important; 
    color:#fff !important; 
    border:none !important; 
    border-radius:8px !important; 
    padding:10px 18px !important; 
    font-weight:900 !important;
}
.btn-secondary { 
    background:#936037 !important; 
    color:#fff !important; 
    border:none !important; 
    border-radius:8px !important; 
    padding:10px 18px !important; 
    font-weight:900 !important;
}
.product-header {
    background:#ff9b2f;
    padding:12px;
    border-radius:8px;
    margin-bottom:15px;
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

# ===== Obtener ID y datos del producto =====
product_id = get_product_id()
if not product_id:
    st.error("No se recibió un ID de producto para editar.")
    st.stop()

product = fetch_product(product_id)
if not product:
    st.stop()

# Defaults con fallback
name        = product.get("name", "Producto sin nombre")
category    = product.get("category", "")
subcategory = product.get("subcategory", "")
stock       = int(product.get("stock", 0) or 0)
price       = int(product.get("price", 0) or 0)
image_url   = product.get("image_url", "") or ""
description = product.get("description", "") or ""
features    = product.get("features", "") or ""
rating      = float(product.get("rating", 0.0) or 0.0)
sold        = int(product.get("sold", 0) or 0)

pay_method_value = product.get("pay_method") or "Transferencia Bancaria"
network_value    = product.get("network") or "BEP-20"
alias_value      = product.get("alias") or ""
wallet_value     = product.get("wallet") or ""

# ===== Encabezado =====
st.markdown('<div class="hdr"><h3>✏️ EDITAR PRODUCTO</h3></div>', unsafe_allow_html=True)
st.markdown('<div class="panel">', unsafe_allow_html=True)

# Header de producto
st.markdown("<div class='product-header'>", unsafe_allow_html=True)
col_info1, col_info2 = st.columns([1, 3])
with col_info1:
    if image_url:
        try:
            st.image(image_url, use_container_width=True)
        except Exception:
            st.markdown(
                '<div style="background:#f8f9fa; border-radius:8px; padding:40px 20px; text-align:center; border:1px solid #ddd;">'
                '<span style="color:#666;">📸</span>'
                '</div>',
                unsafe_allow_html=True
            )
    else:
        st.markdown(
            '<div style="background:#f8f9fa; border-radius:8px; padding:40px 20px; text-align:center; border:1px solid #ddd;">'
            '<span style="color:#666;">📸</span>'
            '</div>', 
            unsafe_allow_html=True
        )
with col_info2:
    st.markdown(f"### {name}")
    st.markdown(
        f"**🏪 Vendedor:** {product.get('seller_alias','(sin alias)')} • "
        f"**⭐ Valoración:** {rating:.1f}/10 • "
        f"**🎯 Ventas:** {sold} unidades"
    )
    st.markdown(
        f"**📂 Categoría:** {category or '-'} • "
        f"**🔍 Subcategoría:** {subcategory or '-'}"
    )
st.markdown("</div>", unsafe_allow_html=True)

# ===== Formulario completo =====
with st.form("edit_product_form"):
    # --- Info básica ---
    st.markdown('<div class="section-title">📝 INFORMACIÓN BÁSICA</div>', unsafe_allow_html=True)
    col_basic1, col_basic2 = st.columns(2)
    with col_basic1:
        product_name = st.text_input("Nombre del producto", value=name, key="name")
        product_category = st.text_input("Categoría", value=category, key="category")
        product_subcategory = st.text_input("Subcategoría", value=subcategory, key="subcategory")
    with col_basic2:
        product_stock = st.number_input("Stock disponible", min_value=0, value=stock, step=1, key="stock")
        product_price = st.number_input("Precio unitario ($)", min_value=0, value=price, step=100, key="price")
        product_image = st.text_input("URL de imagen", value=image_url, key="image")

    # --- Descripción / características ---
    st.markdown('<div class="section-title">📋 DESCRIPCIÓN Y CARACTERÍSTICAS</div>', unsafe_allow_html=True)
    product_description = st.text_area(
        "Descripción breve del producto",
        value=description,
        height=100,
        key="description"
    )

    product_features = st.text_area(
        "Características técnicas",
        value=features,
        height=120,
        key="features"
    )

    # --- Configuración de pagos (se guarda en pay_method, alias, network, wallet) ---
    st.markdown('<div class="section-title">💳 CONFIGURACIÓN DE PAGOS</div>', unsafe_allow_html=True)

    payment_options = ["Transferencia Bancaria", "Mercado Pago", "Tarjeta de Crédito", "Criptomonedas"]
    network_options  = ["BEP-20", "ERC-20", "TRC-20", "Polygon"]

    def idx_or_default(value, options, default_index=0):
        try:
            return options.index(value)
        except ValueError:
            return default_index

    col_payment1, col_payment2 = st.columns(2)
    with col_payment1:
        payment_method = st.selectbox(
            "Método de pago principal",
            payment_options,
            index=idx_or_default(pay_method_value, payment_options),
            key="pay_method"
        )
        payment_alias = st.text_input("Alias/CBU", value=alias_value, key="alias")
    with col_payment2:
        crypto_network = st.selectbox(
            "Red para criptomonedas",
            network_options,
            index=idx_or_default(network_value, network_options),
            key="network"
        )
        crypto_wallet = st.text_input("Wallet address", value=wallet_value, key="wallet")

    # --- Información adicional (solo UI, no DB a menos que quieras añadir campos nuevos) ---
    st.markdown('<div class="section-title">📊 INFORMACIÓN ADICIONAL</div>', unsafe_allow_html=True)
    col_extra1, col_extra2 = st.columns(2)
    with col_extra1:
        product_condition = st.selectbox(
            "Condición del producto",
            ["Nuevo", "Como nuevo", "Usado - Excelente", "Usado - Bueno"],
            index=0,
            key="condition"
        )
        product_weight = st.number_input("Peso (kg)", min_value=0.0, value=0.5, step=0.1, key="weight")
    with col_extra2:
        product_dimensions = st.text_input("Dimensiones (LxAxA cm)", value="30x20x5", key="dimensions")
        shipping_time = st.number_input("Tiempo de envío (días)", min_value=1, value=3, step=1, key="shipping_time")

    st.markdown("---")
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    with col_btn1:
        save_click = st.form_submit_button("💾 GUARDAR CAMBIOS", use_container_width=True)
    with col_btn2:
        reset_click = st.form_submit_button("🔄 RESTABLECER", use_container_width=True)
    with col_btn3:
        back_click = st.form_submit_button("⬅️ VOLVER A MIS PRODUCTOS", use_container_width=True)

if save_click:
    payload = {
        "name": product_name,
        "category": product_category,
        "subcategory": product_subcategory,
        "stock": int(product_stock),
        "price": int(product_price),
        "image_url": product_image or None,
        "description": product_description or None,
        "features": product_features or None,
        # pagos / cripto
        "pay_method": payment_method,
        "alias": payment_alias or None,
        "network": crypto_network,
        "wallet": crypto_wallet or None,
        # preservamos seller_id y seller_alias si venían del backend
        "seller_id": product.get("seller_id"),
        "seller_alias": product.get("seller_alias"),
    }
    update_product(product_id, payload)

if reset_click:
    # Simplemente recarga la página y vuelve a traer los datos desde el backend
    st.rerun()

if back_click:
    # Volver a Mis Productos
    st.switch_page("pages/7_📦_Mis_Productos.py")

# ===== Vista previa =====
with st.expander("👁️ VISTA PREVIA DEL PRODUCTO"):
    st.markdown(f"### {product_name}")
    col_preview1, col_preview2 = st.columns([1, 2])
    with col_preview1:
        if product_image:
            try:
                st.image(product_image, use_container_width=True)
            except Exception:
                st.markdown(
                    '<div style="background:#f8f9fa; border-radius:8px; padding:60px 30px; text-align:center; border:1px solid #ddd;">'
                    '<span style="color:#666;">Imagen del Producto</span>'
                    '</div>', 
                    unsafe_allow_html=True
                )
        else:
            st.markdown(
                '<div style="background:#f8f9fa; border-radius:8px; padding:60px 30px; text-align:center; border:1px solid #ddd;">'
                '<span style="color:#666;">Imagen del Producto</span>'
                '</div>', 
                unsafe_allow_html=True
            )
    with col_preview2:
        st.markdown(f"**Precio:** ${product_price:,}".replace(",", "."))
        st.markdown(f"**Stock:** {product_stock} unidades")
        st.markdown(f"**⭐ {rating:.1f}/10** ({sold} valoraciones)")
        st.markdown(f"**Envío estimado:** {shipping_time} días hábiles")

    st.markdown("**Descripción:**")
    st.write(product_description)

    st.markdown("**Características:**")
    for line in (product_features or "").splitlines():
        if line.strip():
            st.write(line)

st.markdown('</div>', unsafe_allow_html=True)  # /panel
