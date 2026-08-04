import streamlit as st

# PALETA NEUTRA (sin identidad de marca de un cliente específico) --------
COLOR_PRIMARY = "#1E3A5F"        # azul marino, color de acento principal
COLOR_PRIMARY_DARK = "#152A45"   # azul marino oscuro (hover/énfasis)
COLOR_BG = "#EAF1F8"             # fondo general, azul pálido suave
COLOR_CARD = "#FFFFFF"           # fondo de tarjetas
COLOR_BORDER = "#D6DBE1"         # bordes neutros
COLOR_TEXT = "#0F172A"           # texto principal
COLOR_TEXT_MUTED = "#5B6472"     # texto secundario / subtítulos


def inject_css():
    st.markdown(f"""
    <style>
        /* El tema claro se fija en .streamlit/config.toml ([theme] base="light"),
           que evita que Streamlit genere variables de color oscuras cuando el
           navegador/SO está en Dark Mode. Este bloque es un refuerzo cosmético. */
        html, body {{
            background-color: {COLOR_BG} !important;
            color-scheme: light !important;
        }}

        .stApp, [data-testid="stApp"] {{
            background-color: {COLOR_BG} !important;
        }}

        p, span, div, h1, h2, h3, h4, h5, h6, label {{
            color: {COLOR_TEXT} !important;
        }}

        /* Estilos del header principal */
        .main-title {{
            color: {COLOR_TEXT} !important;
            font-family: 'Roboto', sans-serif;
            font-weight: 900;
            font-size: 2.5rem;
            margin-bottom: 0px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .main-subtitle {{
            color: {COLOR_TEXT_MUTED} !important;
            font-family: 'Roboto', sans-serif;
            font-weight: 500;
            font-size: 1.2rem;
            margin-bottom: 20px;
        }}

        /* Contenedores nativos de Streamlit como tarjetas (Cards) */
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: {COLOR_CARD} !important;
            border-radius: 12px !important;
            box-shadow: 0 4px 10px rgba(15, 23, 42, 0.06) !important;
            border: 1px solid {COLOR_BORDER} !important;
            padding: 5px;
        }}

        /* Inputs y Selectboxes - Forzar fondo claro y borde visible */
        input, select, textarea, div[data-baseweb="select"], div[data-baseweb="input"] {{
            background-color: {COLOR_CARD} !important;
            color: {COLOR_TEXT} !important;
            border: 1px solid #94A3B8 !important;
            border-radius: 6px !important;
        }}
        input::placeholder, textarea::placeholder {{
            color: #64748B !important;
        }}

        /* Botones más grandes para pantallas táctiles */
        div.stButton > button {{
            min-height: 50px;
            border-radius: 8px;
            font-weight: bold;
            font-size: 1.1rem;
            background-color: #F8FAFC !important;
            color: {COLOR_TEXT} !important;
            border: 1px solid {COLOR_BORDER} !important;
        }}
        div.stButton > button[kind="primary"] {{
            background-color: {COLOR_PRIMARY} !important;
            color: #FFFFFF !important;
            border: 1px solid {COLOR_PRIMARY_DARK} !important;
        }}
        div.stButton > button[kind="primary"]:hover {{
            background-color: {COLOR_PRIMARY_DARK} !important;
        }}

        /* Banners de error y warning más impactantes */
        div[data-testid="stAlert"] {{
            border-radius: 8px !important;
            border-left-width: 6px !important;
            font-weight: 600;
            background-color: {COLOR_CARD} !important;
        }}

        /* Pestañas: subrayado activo en azul marino */
        button[data-baseweb="tab"][aria-selected="true"] {{
            color: {COLOR_PRIMARY} !important;
            border-bottom-color: {COLOR_PRIMARY} !important;
        }}

        /* Sidebar de navegación (roles / páginas) */
        [data-testid="stSidebar"] {{
            background-color: {COLOR_CARD} !important;
            border-right: 1px solid {COLOR_BORDER} !important;
        }}
    </style>
    """, unsafe_allow_html=True)
