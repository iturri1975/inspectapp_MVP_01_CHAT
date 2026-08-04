import streamlit as st

from core.state import TAREAS_DISPONIBLES, TAREAS_PROXIMAMENTE

st.subheader(":material/engineering: Configuración de Obra")

with st.container(border=True):
    col_cfg1, col_cfg2, col_cfg3 = st.columns(3)
    with col_cfg1:
        st.session_state.obra_seleccionada = st.selectbox(
            "Estación / Tramo",
            ["Medanito", "Allen", "Crucero Catriel", "Puerto Rosales"],
            index=["Medanito", "Allen", "Crucero Catriel", "Puerto Rosales"].index(st.session_state.obra_seleccionada),
        )
    with col_cfg2:
        st.session_state.inspector = st.text_input("Inspector", st.session_state.inspector)
    with col_cfg3:
        st.session_state.solicitante_contratista = st.text_input(
            "Solicitante Contratista", st.session_state.solicitante_contratista
        )

with st.container(border=True):
    st.write("**Tarea a realizar**")
    opciones_tarea = TAREAS_DISPONIBLES + [f"{t} (próximamente)" for t in TAREAS_PROXIMAMENTE]
    seleccion = st.selectbox(
        "Tarea",
        opciones_tarea,
        label_visibility="collapsed",
        key="select_tarea",
    )
    if seleccion in TAREAS_DISPONIBLES:
        st.session_state.tarea_seleccionada = seleccion
        st.success(f"Tarea habilitada: {seleccion}. Continuá a Momento 1 en el menú de la izquierda.", icon=":material/check_circle:")
    else:
        st.session_state.tarea_seleccionada = None
        st.info(
            "Esta tarea todavía no está disponible en el MVP — por ahora el flujo completo "
            "solo está desarrollado para Excavación.",
            icon=":material/hourglass_empty:",
        )

with st.container(border=True):
    st.write("**Tipo de permiso**")
    tipo = st.radio(
        "Tipo de permiso",
        ["Frío", "Caliente"],
        index=None if st.session_state.tipo_permiso is None else ["Frío", "Caliente"].index(st.session_state.tipo_permiso),
        label_visibility="collapsed",
        horizontal=True,
        key="radio_tipo_permiso",
    )
    st.session_state.tipo_permiso = tipo
    if tipo == "Frío":
        st.caption("Trabajo en frío: la verificación de gases queda deshabilitada en Momento 1.")
    elif tipo == "Caliente":
        st.caption("Trabajo en caliente: se exige medición de gases y reverificación cada 60 minutos en Momento 1.")
    else:
        st.warning("Seleccioná el tipo de permiso para continuar.", icon=":material/warning:")
