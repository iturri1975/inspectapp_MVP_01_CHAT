import streamlit as st

from core.state import init_state
from core.styles import inject_css, COLOR_PRIMARY

st.set_page_config(
    page_title="INSPECTAPP MVP 2",
    page_icon="⛑️",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_state()
inject_css()

LOGO_MARK_HTML = f"""
<div style="display:flex;align-items:center;justify-content:center;
            width:64px;height:64px;border-radius:16px;margin:0 auto;
            background-color:{COLOR_PRIMARY};">
    <svg width="34" height="34" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path d="M4 15 A8 8 0 0 1 20 15 Z" fill="#FFFFFF"/>
        <rect x="2" y="14.5" width="20" height="3" rx="1.5" fill="#FFFFFF"/>
        <rect x="11" y="4" width="2" height="3" rx="1" fill="#FFFFFF"/>
    </svg>
</div>
"""

# === SELECTOR DE ROL (login simplificado, sin contraseña) ===
if st.session_state.role is None:
    with st.container(border=True):
        col_logo, col_titles = st.columns([1, 4], vertical_alignment="center")
        with col_logo:
            st.markdown(LOGO_MARK_HTML, unsafe_allow_html=True)
        with col_titles:
            st.markdown("<div class='main-title'>INSPECTAPP</div>", unsafe_allow_html=True)
            st.markdown("<div class='main-subtitle'>Copiloto digital de inspección</div>", unsafe_allow_html=True)

    st.write("")
    st.subheader("¿Con qué rol ingresás?")
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("### :material/engineering: Inspector")
            st.caption("Carga de datos, checklists y evidencias en el frente de obra.")
            if st.button("Ingresar como Inspector", type="primary", key="btn_role_inspector"):
                st.session_state.role = "inspector"
                st.rerun()
    with col2:
        with st.container(border=True):
            st.markdown("### :material/supervisor_account: Referente")
            st.caption("Supervisión remota: notificaciones, auditoría y autorización de desvíos.")
            if st.button("Ingresar como Referente", type="primary", key="btn_role_referente"):
                st.session_state.role = "referente"
                st.rerun()
    st.stop()

# === NAVEGACIÓN POR ROL ===
p_config = st.Page("screens/config_obra.py", title="Configuración de Obra", icon=":material/engineering:")
p_m1 = st.Page("screens/momento1.py", title="Momento 1", icon=":material/assignment:")
p_m2 = st.Page("screens/momento2.py", title="Momento 2", icon=":material/construction:")
p_referente = st.Page("screens/panel_referente.py", title="Panel del Referente", icon=":material/supervisor_account:")

if st.session_state.role == "inspector":
    pages = [p_config, p_m1, p_m2]
else:
    pages = [p_referente]

with st.sidebar:
    st.markdown(LOGO_MARK_HTML, unsafe_allow_html=True)
    st.markdown(f"**Rol activo:** {'Inspector' if st.session_state.role == 'inspector' else 'Referente'}")
    if st.button(":material/swap_horiz: Cambiar de rol", key="btn_swap_role"):
        st.session_state.role = None
        st.rerun()
    st.divider()

pg = st.navigation(pages)
pg.run()
