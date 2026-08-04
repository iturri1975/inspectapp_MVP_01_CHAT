import streamlit as st

from core.content import TIPIFICACION_SUELOS_URL
from core.rules import evaluar_zanja
from core.state import notificar_referente, validar_token

st.subheader(":material/construction: Momento 2 — Inspección Operativa en Campo")

if not st.session_state.tarea_seleccionada:
    st.warning("Primero elegí la tarea en Configuración de Obra.", icon=":material/front_hand:")
    st.stop()

if not st.session_state.m1_habilitado_por_referente:
    st.error(
        "🛑 Momento 2 Bloqueado: el Referente todavía no habilitó el paso a Momento 2. "
        "Completá y enviá el Momento 1 primero.",
        icon=":material/lock:",
    )
    st.stop()

# === EQUIPAMIENTO Y ENTORNO ===
with st.container(border=True):
    st.write("**Equipamiento e Interferencias**")
    col_eq1, col_eq2 = st.columns(2)
    with col_eq1:
        st.session_state.eq_calibracion_vigente = st.checkbox(
            "Equipo de detección con calibración vigente", value=st.session_state.eq_calibracion_vigente
        )
        st.session_state.eq_nombre_deteccion = st.text_input(
            "Nombre / modelo del equipo utilizado (RD, Georadar, etc.)", st.session_state.eq_nombre_deteccion
        )
        st.session_state.cateo_360 = st.checkbox("Cateo manual a 360° realizado", value=st.session_state.cateo_360)
    with col_eq2:
        st.session_state.eq_acopio = st.checkbox("Acopio de material a > 2.00 m del borde", value=st.session_state.eq_acopio)
        st.session_state.eq_clima = st.checkbox("Estabilidad del suelo verificada (sin lluvias)", value=st.session_state.eq_clima)
        st.session_state.eq_delimitacion = st.checkbox(
            "Estacas / demarcación según necesidad de la zona de trabajo", value=st.session_state.eq_delimitacion
        )

    st.divider()
    st.write("**Interferencias identificadas**")
    for i, interf in enumerate(st.session_state.interferencias):
        col_i1, col_i2, col_i3 = st.columns([3, 2, 1])
        with col_i1:
            st.write(f"🔧 {interf['tipo']}")
        with col_i2:
            st.write(f"Profundidad real: {interf['profundidad']:.2f} m")
        with col_i3:
            if st.button("Quitar", key=f"btn_quitar_interf_{i}"):
                st.session_state.interferencias.pop(i)
                st.rerun()

    with st.form("form_interferencia", clear_on_submit=True):
        col_f1, col_f2, col_f3 = st.columns([3, 2, 1])
        with col_f1:
            nuevo_tipo = st.text_input("Tipo de interferencia detectada", key="nuevo_tipo_interferencia")
        with col_f2:
            nueva_prof = st.number_input("Profundidad real (m, cateo manual)", min_value=0.0, step=0.01, key="nueva_prof_interferencia")
        with col_f3:
            st.write("")
            st.write("")
            agregar = st.form_submit_button("➕ Agregar")
        if agregar and nuevo_tipo.strip():
            st.session_state.interferencias.append({"tipo": nuevo_tipo.strip(), "profundidad": nueva_prof})
            st.rerun()

# === ZANJA PROFUNDA ===
with st.container(border=True):
    st.write("**Zanja / Excavación**")
    st.session_state.prof_plan = st.number_input(
        "Profundidad de excavación planificada (m)", min_value=0.0, value=st.session_state.prof_plan, step=0.1
    )

    chk_vigia = chk_escape = chk_no_madera = chk_vallas = chk_arnes = chk_entibado_instalado = False

    if st.session_state.prof_plan > 1.20:
        st.warning("⚠️ PROFUNDIDAD CRÍTICA (> 1.20 m). Controles obligatorios:", icon=":material/warning:")
        col_z1, col_z2 = st.columns(2)
        with col_z1:
            chk_vigia = st.checkbox("Vigía de Retén en exterior")
            chk_escape = st.checkbox("Doble Salida de Escape (< 8 m)")
        with col_z2:
            chk_no_madera = st.checkbox("Vallas perimetrales sin madera")

        st.write("**Entibado**")
        col_e1, col_e2 = st.columns([2, 1])
        with col_e1:
            entibado_opt = st.radio(
                "¿Aplica entibado según tipo de suelo?",
                ["Sí", "No"],
                index=None if st.session_state.entibado_aplica is None else ["Sí", "No"].index(st.session_state.entibado_aplica),
                horizontal=True,
                label_visibility="collapsed",
                key="radio_entibado",
            )
            st.session_state.entibado_aplica = entibado_opt
        with col_e2:
            st.link_button(":material/help: Consultar Tipificación de Suelos", TIPIFICACION_SUELOS_URL)

        if st.session_state.entibado_aplica == "Sí":
            chk_entibado_instalado = st.checkbox("Entibado instalado")

        if st.session_state.prof_plan > 1.50:
            st.warning("🚧 VALLADO OBLIGATORIO (> 1.50 m).", icon=":material/fence:")
            chk_vallas = st.checkbox("Vallas a mínimo 1.00 m del borde")

        if st.session_state.prof_plan > 1.80:
            st.error("🚨 MÁXIMO RIESGO (> 1.80 m).", icon=":material/personal_injury:")
            chk_arnes = st.checkbox("Uso de arnés y cabo de vida certificado")
    else:
        st.success("Profundidad estándar (< 1.20 m).", icon=":material/check:")

    bloqueo_fosa, fosa_err = evaluar_zanja(
        st.session_state.prof_plan, chk_vigia, chk_escape, chk_no_madera,
        st.session_state.entibado_aplica, chk_entibado_instalado, chk_vallas, chk_arnes,
    )
    if bloqueo_fosa:
        st.error("🛑 BLOQUEO DE FOSA\n\n" + "\n\n".join(fosa_err), icon=":material/block:")

# === POSICIONAMIENTO DE MAQUINARIA / OMISIÓN AUTORIZADA ===
with st.container(border=True):
    st.write("**Posicionamiento de Maquinaria**")
    st.session_state.maquinaria_paralela = st.checkbox(
        "Retroexcavadora paralela al ducto", value=st.session_state.maquinaria_paralela
    )
    excavacion_proxima = st.radio("¿Excavación a menos de 1.00 metro?", ["No (Stop Mecánico)", "Sí (requiere Omisión Autorizada)"])

    bloqueo_maq = False
    if excavacion_proxima == "Sí (requiere Omisión Autorizada)":
        st.error("🚨 DESVÍO CRÍTICO: vulneración del Stop Mecánico.", icon=":material/warning:")
        if st.session_state.omision_stop_mecanico_autorizada:
            st.success("🔓 Omisión Autorizada validada. Podés continuar.", icon=":material/lock_open:")
        else:
            st.caption(
                "Comunicate con el Referente de Proyecto y pedile el token de autorización desde su Panel. "
                "El Referente evalúa la situación y te dicta un código de 4 dígitos."
            )
            codigo = st.text_input("Token de Omisión Autorizada", key="input_token_m2")
            if codigo:
                if validar_token(codigo, motivo="Excavación a menos de 1.00 m del ducto — Stop Mecánico"):
                    st.session_state.omision_stop_mecanico_autorizada = True
                    notificar_referente(
                        f"{st.session_state.inspector} validó la Omisión Autorizada (Stop Mecánico) en "
                        f"{st.session_state.obra_seleccionada}.",
                        tipo="desvio",
                    )
                    st.rerun()
                else:
                    bloqueo_maq = True
                    st.error("❌ Token inválido o vencido. Pedile uno nuevo al Referente.")
            else:
                bloqueo_maq = True
    else:
        st.session_state.omision_stop_mecanico_autorizada = False

m2_listo = (
    st.session_state.eq_calibracion_vigente
    and st.session_state.eq_delimitacion
    and st.session_state.cateo_360
    and st.session_state.eq_acopio
    and st.session_state.eq_clima
    and st.session_state.maquinaria_paralela
    and not bloqueo_fosa
    and not bloqueo_maq
)

with st.container(border=True):
    if m2_listo:
        st.balloons()
        st.success("🚀 **¡EXCAVACIÓN AUTORIZADA!**", icon=":material/verified:")
        if st.button("📥 Generar Reporte de Liberación", type="primary"):
            notificar_referente(
                f"{st.session_state.inspector} generó el reporte de liberación de excavación en "
                f"{st.session_state.obra_seleccionada}.",
                tipo="reporte",
            )
            st.success("📄 Reporte consolidado exportado y notificado al Referente.")
    else:
        st.warning("⚠️ Resuelva los bloqueos para habilitar la excavación.", icon=":material/front_hand:")
