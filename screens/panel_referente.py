import datetime

import streamlit as st

from core.state import generar_token

st.subheader(":material/supervisor_account: Panel del Referente")
st.caption("Supervisión remota: notificaciones, auditoría visual y autorización de desvíos.")

# === BANDEJA DE NOTIFICACIONES ===
with st.container(border=True):
    st.write("**Notificaciones**")
    if not st.session_state.notificaciones:
        st.info("Sin notificaciones todavía.", icon=":material/notifications_none:")
    else:
        for n in st.session_state.notificaciones:
            hora = datetime.datetime.fromtimestamp(n["timestamp"]).strftime("%H:%M:%S")
            icono = {"momento1": ":material/assignment_turned_in:", "desvio": ":material/gpp_maybe:", "reporte": ":material/description:"}.get(n["tipo"], ":material/notifications:")
            st.info(f"{hora} — {n['mensaje']}", icon=icono)

# === HABILITACIÓN DE MOMENTO 2 ===
with st.container(border=True):
    st.write("**Habilitación de Momento 2**")
    if not st.session_state.m1_enviado:
        st.caption("El Inspector todavía no envió el Momento 1.")
    else:
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Obra", st.session_state.obra_seleccionada or "—")
            st.metric("Tarea", st.session_state.tarea_seleccionada or "—")
        with col_b:
            st.metric("Inspector", st.session_state.inspector or "—")
            st.metric("Tipo de permiso", st.session_state.tipo_permiso or "—")

        st.write("**Auditoría visual de evidencias**")
        col_ev1, col_ev2, col_ev3, col_ev4 = st.columns(4)
        for col, key, label in [
            (col_ev1, "foto_charla", "Charla 5 min"),
            (col_ev2, "foto_cpt", "CPT"),
            (col_ev3, "foto_permiso_frente", "Permiso — Frente"),
            (col_ev4, "foto_permiso_dorso", "Permiso — Dorso"),
        ]:
            with col:
                if st.session_state[key] is not None:
                    st.image(st.session_state[key], caption=label, width="stretch")
                else:
                    st.caption(f"{label}: sin adjuntar")

        if st.session_state.m1_habilitado_por_referente:
            st.success("Momento 2 ya habilitado.", icon=":material/verified:")
        else:
            if st.button("✅ Habilitar Momento 2", type="primary"):
                st.session_state.m1_habilitado_por_referente = True
                st.rerun()

# === MOTOR DE DESVÍOS: GENERACIÓN DE TOKENS ===
with st.container(border=True):
    st.write("**Omisión Autorizada — Generar token**")
    st.caption("Evaluá la situación con el Inspector y, si corresponde, generá un token de 4 dígitos para dictarle por teléfono.")
    if st.session_state.token_activo:
        st.warning(
            f"Token activo sin usar: **{st.session_state.token_activo}**",
            icon=":material/pending:",
        )
    if st.button("🔑 Generar nuevo token"):
        generar_token()
        st.rerun()

    if st.session_state.desvios:
        st.write("**Historial de Omisiones Autorizadas**")
        for d in st.session_state.desvios:
            hora = datetime.datetime.fromtimestamp(d["timestamp"]).strftime("%d/%m %H:%M")
            st.write(f"- `{hora}` — {d['motivo']} (token {d['token']})")
