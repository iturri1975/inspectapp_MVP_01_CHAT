import time

import streamlit as st

from core.rules import evaluar_gases, evaluar_sertronic
from core.state import GAS_RECHECK_INTERVAL_SECONDS, notificar_referente
from core.ui import evidencia_uploader

st.subheader(":material/assignment: Momento 1 — Verificación Documental")

if not st.session_state.tarea_seleccionada:
    st.warning(
        "Primero elegí la tarea y el tipo de permiso en Configuración de Obra.",
        icon=":material/front_hand:",
    )
    st.stop()

if not st.session_state.tipo_permiso:
    st.warning("Falta seleccionar el tipo de permiso (Frío/Caliente) en Configuración de Obra.", icon=":material/front_hand:")
    st.stop()

# === CONSULTA AUTOMATIZADA SERTRONIC (mock) ===
with st.container(border=True):
    st.write("**Verificación Documental**")
    col_doc1, col_doc2 = st.columns(2)
    with col_doc1:
        st.session_state.num_permiso = st.text_input("N° Permiso (Sertronic)", st.session_state.num_permiso)
    with col_doc2:
        st.session_state.num_cpt = st.text_input("N° CPT Asociado (Blister)", st.session_state.num_cpt)

    st.write("**Consulta Automatizada de Habilitaciones (Sertronic)**")
    st.caption("Simulación binaria por recurso, previa a la conexión técnica definitiva con la API de Sertronic.")
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.session_state.sertronic_personal = st.selectbox(
            "Personal", ["Verde", "Rojo"],
            index=["Verde", "Rojo"].index(st.session_state.sertronic_personal),
        )
    with col_s2:
        st.session_state.sertronic_vehiculos = st.selectbox(
            "Vehículos", ["Verde", "Rojo"],
            index=["Verde", "Rojo"].index(st.session_state.sertronic_vehiculos),
        )
    with col_s3:
        st.session_state.sertronic_maquinaria = st.selectbox(
            "Maquinaria", ["Verde", "Rojo"],
            index=["Verde", "Rojo"].index(st.session_state.sertronic_maquinaria),
        )

    bloqueo_sertronic, detalle_sertronic = evaluar_sertronic(
        st.session_state.sertronic_personal,
        st.session_state.sertronic_vehiculos,
        st.session_state.sertronic_maquinaria,
    )
    if bloqueo_sertronic:
        recursos_rojos = [k for k, v in detalle_sertronic.items() if v == "Rojo"]
        st.error(
            "🛑 BLOQUEO DE SEGURIDAD (HARD GATE)\n\n"
            f"Documentación vencida o faltante en: {', '.join(recursos_rojos)}. "
            "Andá a Sertronic y solicitá la regularización a la contratista.",
            icon=":material/block:",
        )
    else:
        st.success("Habilitaciones vigentes. Personal, vehículos y maquinaria en regla.", icon=":material/check_circle:")

# === CONTROL DE GASES (solo trabajo en caliente) ===
bloqueo_gases = False
if st.session_state.tipo_permiso == "Caliente":
    with st.container(border=True):
        st.write("**Control Crítico de Gases**")
        col_g1, col_g2, col_g3, col_g4 = st.columns(4)
        with col_g1:
            st.session_state.gases["lel"] = st.number_input(
                "L.E.L (%)", min_value=0.0, max_value=100.0, value=st.session_state.gases["lel"], step=0.1
            )
        with col_g2:
            st.session_state.gases["o2"] = st.number_input(
                "O2 (%)", min_value=0.0, max_value=100.0, value=st.session_state.gases["o2"], step=0.1
            )
        with col_g3:
            st.session_state.gases["co"] = st.number_input(
                "CO (ppm)", min_value=0.0, max_value=1000.0, value=st.session_state.gases["co"], step=1.0
            )
        with col_g4:
            st.session_state.gases["h2s"] = st.number_input(
                "H2S (ppm)", min_value=0.0, max_value=500.0, value=st.session_state.gases["h2s"], step=1.0
            )

        bloqueo_gases, gases_err = evaluar_gases(
            st.session_state.gases["lel"], st.session_state.gases["o2"],
            st.session_state.gases["co"], st.session_state.gases["h2s"],
        )
        if bloqueo_gases:
            st.error("🛑 BLOQUEO DE SEGURIDAD (HARD GATE)\n\n" + "\n\n".join(gases_err), icon=":material/block:")
        else:
            st.success("Atmósfera segura. Valores dentro del rango tolerado.", icon=":material/check_circle:")

        col_rec1, col_rec2 = st.columns([3, 1])
        with col_rec1:
            if st.session_state.gases_ultima_verificacion is None:
                st.info("Todavía no registraste la verificación inicial de gases.", icon=":material/schedule:")
            else:
                restante = GAS_RECHECK_INTERVAL_SECONDS - (time.time() - st.session_state.gases_ultima_verificacion)
                if restante <= 0:
                    st.warning("⏰ Corresponde re-verificar la atmósfera (pasaron más de 60 minutos).", icon=":material/notifications_active:")
                else:
                    minutos, segundos = divmod(int(restante), 60)
                    st.info(f"Próxima re-verificación en: {minutos:02d}:{segundos:02d}", icon=":material/schedule:")
        with col_rec2:
            if st.button("Verificar ahora", key="btn_verificar_gases"):
                st.session_state.gases_ultima_verificacion = time.time()
                st.rerun()
else:
    st.caption("Trabajo en frío: la medición de gases no aplica para este permiso.")

# === FIRMAS Y EVIDENCIA FOTOGRÁFICA ===
with st.container(border=True):
    st.write("**Firmas y Evidencia (Momento 1)**")
    st.session_state.cpt_checked = st.checkbox(
        "Certifico bajo declaración jurada haber brindado la charla de 5 minutos y verificado el CPT en físico.",
        value=st.session_state.cpt_checked,
    )

    col_ev1, col_ev2 = st.columns(2)
    with col_ev1:
        ok_charla = evidencia_uploader("Charla de 5 minutos", "foto_charla", "upload_charla")
    with col_ev2:
        ok_cpt = evidencia_uploader("Planilla CPT firmada", "foto_cpt", "upload_cpt")

    col_ev3, col_ev4 = st.columns(2)
    with col_ev3:
        ok_frente = evidencia_uploader("Permiso de Trabajo — Frente", "foto_permiso_frente", "upload_permiso_frente")
    with col_ev4:
        ok_dorso = evidencia_uploader("Permiso de Trabajo — Dorso", "foto_permiso_dorso", "upload_permiso_dorso")

    evidencias_completas = ok_charla and ok_cpt and ok_frente and ok_dorso

    st.session_state.firma_inspector_m1 = st.checkbox(
        f"Firma: {st.session_state.inspector} (Inspector)",
        value=st.session_state.firma_inspector_m1,
        disabled=bloqueo_sertronic or bloqueo_gases or not st.session_state.cpt_checked or not evidencias_completas,
    )

m1_listo = (
    st.session_state.firma_inspector_m1
    and not bloqueo_sertronic
    and not bloqueo_gases
    and evidencias_completas
)

with st.container(border=True):
    if not m1_listo:
        faltantes = []
        if bloqueo_sertronic:
            faltantes.append("regularizar habilitaciones en Sertronic")
        if bloqueo_gases:
            faltantes.append("resolver el bloqueo de gases")
        if not evidencias_completas:
            faltantes.append("adjuntar las 4 evidencias fotográficas")
        if not st.session_state.cpt_checked:
            faltantes.append("certificar la charla/CPT")
        st.warning("Faltan pasos para completar Momento 1: " + "; ".join(faltantes) + ".", icon=":material/warning:")
    elif not st.session_state.m1_enviado:
        st.success("Momento 1 completo. Enviá la notificación al Referente para poder pasar a Momento 2.", icon=":material/done_all:")
        if st.button("📤 Enviar Momento 1 al Referente", type="primary"):
            st.session_state.m1_enviado = True
            notificar_referente(
                f"{st.session_state.inspector} completó el Momento 1 en {st.session_state.obra_seleccionada} "
                f"({st.session_state.tarea_seleccionada}, permiso {st.session_state.tipo_permiso}). "
                "Pendiente de habilitación para pasar a Momento 2.",
                tipo="momento1",
            )
            st.rerun()
    elif not st.session_state.m1_habilitado_por_referente:
        st.info("Momento 1 enviado. Esperando que el Referente habilite el paso a Momento 2.", icon=":material/hourglass_top:")
    else:
        st.success("✅ Momento 2 habilitado por el Referente. Podés continuar en el menú de la izquierda.", icon=":material/verified:")
