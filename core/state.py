import random
import time

import streamlit as st

TAREAS_DISPONIBLES = ["Excavación"]
TAREAS_PROXIMAMENTE = ["Izaje", "Trabajos en Altura", "Soldadura"]

GAS_RECHECK_INTERVAL_SECONDS = 60 * 60  # 60 minutos


def init_state():
    """Inicializa todo el estado compartido entre pantallas con valores por defecto.
    Idempotente: no pisa valores ya existentes en session_state."""
    defaults = {
        # Rol / navegación
        "role": None,
        # Configuración de obra
        "obra_seleccionada": "Medanito",
        "tarea_seleccionada": None,
        "inspector": "Sofía Cervantes (Ingeniería)",
        "solicitante_contratista": "Ing. Pedro Gómez",
        "num_permiso": "PT-2026-8942",
        "num_cpt": "CPT-4402",
        "tipo_permiso": None,  # "Frío" | "Caliente"
        # Sertronic (mock verde/rojo por recurso)
        "sertronic_personal": "Verde",
        "sertronic_vehiculos": "Verde",
        "sertronic_maquinaria": "Verde",
        # Gases
        "gases": {"lel": 0.0, "o2": 20.9, "co": 0.0, "h2s": 0.0},
        "gases_ultima_verificacion": None,  # epoch seconds
        # Momento 1: evidencias obligatorias
        "cpt_checked": False,
        "foto_charla": None,
        "foto_cpt": None,
        "foto_permiso_frente": None,
        "foto_permiso_dorso": None,
        "firma_inspector_m1": False,
        "m1_enviado": False,  # inspector completó M1 y notificó al referente
        "m1_habilitado_por_referente": False,  # referente habilitó el pase a M2
        # Momento 2
        "eq_nombre_deteccion": "",
        "eq_calibracion_vigente": False,
        "eq_acopio": False,
        "eq_clima": False,
        "cateo_360": False,
        "eq_delimitacion": False,  # estacas/demarcación "según necesidad"
        "interferencias": [],  # list[{"tipo": str, "profundidad": float}]
        "prof_plan": 1.0,
        "entibado_aplica": None,  # "Sí" | "No" | None (sin definir)
        "maquinaria_paralela": False,
        # Motor de desvíos (Omisión Autorizada)
        "token_activo": None,
        "token_motivo": None,
        "token_generado_en": None,
        "desvios": [],  # log de omisiones autorizadas
        "omision_stop_mecanico_autorizada": False,  # se fija en True una vez validado el token en Momento 2
        # Notificaciones al referente
        "notificaciones": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def notificar_referente(mensaje: str, tipo: str = "info"):
    """Agrega una notificación a la bandeja del Referente (simulada en session_state)."""
    st.session_state.notificaciones.insert(0, {
        "mensaje": mensaje,
        "tipo": tipo,
        "timestamp": time.time(),
        "leida": False,
    })


def generar_token() -> str:
    """Genera un token numérico de 4 dígitos y lo deja activo para que el Inspector lo valide."""
    token = f"{random.randint(0, 9999):04d}"
    st.session_state.token_activo = token
    st.session_state.token_generado_en = time.time()
    return token


def validar_token(intento: str, motivo: str) -> bool:
    """Valida el token ingresado por el Inspector contra el token activo generado por el Referente.
    Si es válido, lo consume (single-use) y deja registro en el log de desvíos."""
    if st.session_state.token_activo and intento == st.session_state.token_activo:
        st.session_state.desvios.append({
            "motivo": motivo,
            "token": intento,
            "timestamp": time.time(),
        })
        st.session_state.token_activo = None
        st.session_state.token_generado_en = None
        return True
    return False
