import streamlit as st
import google.generativeai as genai
import pandas as pd
import os
import base64

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="INSPECTAPP MVP v5.0",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Convertir avatar local a base64 para CSS
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

ivo_b64 = get_image_base64("./IVO.png")
ivo_bg_css = f"url('data:image/png;base64,{ivo_b64}')" if ivo_b64 else "none"

# ESTILOS CSS PERSONALIZADOS - ALTO CONTRASTE PARA LUZ SOLAR
st.markdown(f"""
<style>
    /* Ocultar sidebar por completo */
    [data-testid="stSidebar"] {{
        display: none !important;
    }}
    [data-testid="collapsedControl"] {{
        display: none !important;
    }}

    /* El tema claro se fija en .streamlit/config.toml ([theme] base="light"),
       que es lo que evita que Streamlit genere variables de color oscuras
       cuando el navegador/SO está en Dark Mode (afecta también a los
       popovers, menús y demás componentes BaseWeb renderizados en portales).
       Este bloque de CSS es solo un refuerzo cosmético de alto contraste. */
    html, body {{
        background-color: #F4F6F8 !important;
        color-scheme: light !important;
    }}

    .stApp, [data-testid="stApp"] {{
        background-color: #F4F6F8 !important;
    }}

    p, span, div, h1, h2, h3, h4, h5, h6, label {{
        color: #0F172A !important;
    }}

    /* Chat específico: fondo claro para legibilidad absoluta */
    [data-testid="stChatMessage"] {{
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border-radius: 8px !important;
        padding: 10px !important;
        border: 1px solid #CBD5E1 !important;
        margin-bottom: 10px !important;
    }}
    [data-testid="stChatInput"] {{
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 1px solid #94A3B8 !important;
    }}
    [data-testid="stChatInput"] textarea {{
        color: #0F172A !important;
    }}

    /* Estilos del header principal */
    .main-title {{
        color: #0F172A !important;
        font-family: 'Roboto', sans-serif;
        font-weight: 900;
        font-size: 2.5rem;
        margin-bottom: 0px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    .main-subtitle {{
        color: #1E293B !important;
        font-family: 'Roboto', sans-serif;
        font-weight: 500;
        font-size: 1.2rem;
        margin-bottom: 20px;
    }}

    /* Modificando los contenedores nativos de Streamlit para que parezcan tarjetas (Cards) */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: #FFFFFF !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08) !important;
        border: 1px solid #CBD5E1 !important;
        padding: 5px;
    }}

    /* Inputs y Selectboxes - Forzar fondo claro y borde visible */
    input, select, textarea, div[data-baseweb="select"], div[data-baseweb="input"] {{
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 1px solid #94A3B8 !important;
        border-radius: 6px !important;
    }}

    /* Color de texto dentro de inputs y placeholders */
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
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
    }}
    
    div.stButton > button[kind="primary"] {{
        background-color: #0077C8 !important;
        color: #FFFFFF !important;
    }}

    /* Banners de error y warning más impactantes */
    div[data-testid="stAlert"] {{
        border-radius: 8px !important;
        border-left-width: 6px !important;
        font-weight: 600;
        background-color: #FFFFFF !important;
    }}

    /* === ESTILO CABEZA FLOTANTE DE IVO (FAB) === */
    /* Posicionamiento fijo del contenedor del popover al inferior derecho */
    div[data-testid="stPopover"] {{
        position: fixed !important;
        bottom: 25px !important;
        right: 25px !important;
        z-index: 999999 !important; /* Estricto para móviles */
        pointer-events: auto !important; /* Garantizar eventos táctiles */
    }}
    /* Eliminar el selector de hijo directo (>) para apuntar a cualquier botón dentro del popover */
    div[data-testid="stPopover"] button {{
        width: 80px !important;
        height: 80px !important;
        border-radius: 50% !important;
        border: 4px solid #FFFFFF !important;
        box-shadow: 0 8px 24px rgba(0, 119, 200, 0.6) !important;
        background-image: {ivo_bg_css} !important;
        background-color: #0077C8 !important;
        background-size: cover !important;
        background-position: center !important;
        background-repeat: no-repeat !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
        cursor: pointer !important;
        pointer-events: auto !important; /* Garantizar eventos táctiles */
        -webkit-tap-highlight-color: transparent !important; /* Quitar parpadeo en móviles */
    }}
    div[data-testid="stPopover"] button:hover {{
        transform: scale(1.1) !important;
        box-shadow: 0 12px 30px rgba(0, 119, 200, 0.8) !important;
    }}
    /* Ocultar texto dentro del botón FAB */
    div[data-testid="stPopover"] button p,
    div[data-testid="stPopover"] button span,
    div[data-testid="stPopover"] button div {{
        opacity: 0 !important;
        font-size: 0px !important;
    }}
</style>
""", unsafe_allow_html=True)

# INICIALIZACIÓN DEL CHATBOT DE GEMINI Y ESTADO DE EVIDENCIAS
if "messages" not in st.session_state:
    st.session_state.messages = []
if "foto_cpt" not in st.session_state:
    st.session_state.foto_cpt = None
if "foto_cateo" not in st.session_state:
    st.session_state.foto_cateo = None

# Configuración del modelo Gemini utilizando st.secrets o variables de entorno
api_key = None
try:
    api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", None))
except Exception:
    api_key = os.environ.get("GEMINI_API_KEY", None)

model_initialized = False

# System Prompt estructurado con Grounding Estricto y Reglas Oficiales de Oldelval
system_instruction = (
    "Eres Ivo, el Co-piloto Digital Inteligente de INSPECTAPP para los inspectores de campo de Oldelval.\n"
    "Tu objetivo es brindar soporte técnico en tiempo real con 100% de rigor normativo, eliminando alucinaciones e inferencias no autorizadas.\n\n"

    "REGLA N° 1: RIGOR DE FUENTE ÚNICA (GROUNDING ESTRICTO)\n"
    "- Responde ÚNICAMENTE con datos extraídos textualmente de los procedimientos oficiales de Oldelval (normativa en ./docs/).\n"
    "- Si un parámetro (distancias, gases, tiempos, medidas, profundidades) no está explícito en la normativa oficial de Oldelval, debes responder EXACTAMENTE: "
    "\"Ese dato no está especificado en el procedimiento oficial, por favor consulta con el responsable de SSHMA.\"\n"
    "- Queda ESTRICTAMENTE PROHIBIDO inferir, suponer o estimar distancias de seguridad o parámetros técnicos que no figuren en los documentos.\n\n"

    "REGLA N° 2: DISAMBIGUACIÓN DE LER (LISTAS ESPECÍFICAS DE RIESGO)\n"
    "- Cuando te pregunten por la LER (Lista Específica de Riesgo) de cualquier tarea (ej. Excavaciones), DEBES volcar la lista exacta de preguntas y verificaciones del formulario oficial (ej. PO_OL_EIR_03_FO_06 para Excavaciones).\n"
    "- DEBES aclarar siempre de forma inicial que son verificaciones obligatorias 'SÍ/NO/NA' que el Emisor del Permiso de Trabajo y el Solicitante de la contratista deben completar en conjunto y firmar antes de dar inicio a la tarea.\n\n"

    "REGLA N° 3: LISTA ESPECÍFICA DE RIESGO - TAREAS DE EXCAVACIONES (FORMULARIO PO_OL_EIR_03_FO_06):\n"
    "Cuando soliciten la LER de Excavación, enumera textualmente sus 15 ítems obligatorios:\n"
    "• Ítem 1: Verificación de traza y cotas para evitar interferencias con caños y cañeros eléctricos enterrados.\n"
    "• Ítem 2: Utilización de equipamiento específico de detección (detectores de metales, flujo, RD7000) ante interferencias no ubicadas.\n"
    "• Ítem 3: Establecimiento de cateo manual de líneas subterráneas a 360° y señalización posterior.\n"
    "• Ítem 4: Provisión de chalecos reflectantes y banderillas de peligro para trabajadores expuestos a tráfico vehicular.\n"
    "• Ítem 5: Acopio de material: Debe realizarse obligatoriamente como mínimo a **2.00 metros** del borde de la excavación para no causar riesgo al personal en el interior.\n"
    "• Ítem 6: Análisis previo del tipo de suelo para definir las medidas de protección necesarias.\n"
    "• Ítem 7: Inspección diaria obligatoria de excavaciones, fosas y áreas adyacentes por un supervisor experimentado.\n"
    "• Ítem 8: Repetición obligatoria de la inspección en caso de lluvias, filtraciones, nevadas u otras circunstancias que alteren la estabilidad.\n"
    "• Ítem 9: Señalización de todo el perímetro a una distancia mínima de **1.00 metro** del borde, utilizando VALLAS obligatoriamente si la profundidad supera los **1.50 metros**.\n"
    "• Ítem 10: Colocación de escaleras de mano, rampas u otro medio de salida seguro cuando la profundidad exceda los **1.20 metros**, ubicados para que el traslado máximo hasta la salida no supere los **8.00 metros**.\n"
    "• Ítem 11: Señalización de advertencia para excavaciones que queden abiertas o sin vigilancia fuera del horario de trabajo.\n"
    "• Ítem 12: Colocación de carteles reflectantes de advertencia a **200.00 metros** antes en ambas direcciones de tránsito, más vallado y balizas nocturnas.\n"
    "• Ítem 13: Medición de atmósfera explosiva e identificación de gases tóxicos/oxígeno (LEL **0%**, O2 **19.5% - 23.5%**, CO máx **25 ppm**, H2S máx **10 ppm**) según procedimiento de Espacios Confinados.\n"
    "• Ítem 14: Verificación de que no se trabaje con agua acumulada o en aumento sin precauciones de seguridad como equipos de remoción de agua (bombas de desagote).\n"
    "• Ítem 15: Inspección obligatoria de los equipos de remoción de agua y operaciones de desagote por Supervisor especializado para prevenir socavones o derrumbes.\n\n"

    "REGLA N° 4: REGLAS TÉCNICAS ADICIONALES DE OLDELVAL:\n"
    "- Tapada Real (IT_OL_PDD_04): Ecuación matemática **T = D_medida - R_cañería** (Rotular T físicamente en la estaca).\n"
    "- Colores de Estacado (IT_OL_PDD_04):\n"
    "  • Superior Negra / Cuerpo Amarillo: Instalación a descubrir/intervenir con excavación mecánica posterior.\n"
    "  • Superior Roja / Cuerpo Blanco: Interferencia o cruce (excavación mecánica BLOQUEADA a menos de **1.00 metro**).\n"
    "  • Blanco absoluto: Instalación paralela de referencia de proximidad (nunca se excava).\n"
    "- Maquinaria y Stop Mecánico (PO_OL_PDD_01 / PO_OL_EIR_08):\n"
    "  • Retroexcavadora con herramienta paralela al ducto y visión 100% libre u operador con señalero.\n"
    "  • Stop Mecánico a **1.00 metro** del ducto. Para excavar a menos de 1m se requiere cateo manual a 360° en **1.00 metro** de ancho a cada lado y código de Supervisor (**1234**) o reporte de desvío fotográfico.\n"
    "- Zanja Profunda:\n"
    "  • Profundidad > **1.20 metros**: Entibados/apuntalamientos instalados desde el exterior, Vigía de Retén afuera con autónomo, Doble Salida de Escape (traslado < **8.00 metros**). Prohibido usar madera como vallado rígido.\n"
    "  • Profundidad > **1.80 metros**: Arnés de cuerpo completo y cabo de vida amarrado a punto fijo exterior certificado.\n\n"

    "REGLA N° 5: FORMATO DE RESPUESTA PARA CAMPO\n"
    "- Usa viñetas estructuradas y resalta SIEMPRE todas las cifras, distancias y valores en **negrita** para rápida auditoría en terreno."
)

gemini_config_error = None
if api_key:
    try:
        genai.configure(api_key=api_key)
        try:
            model = genai.GenerativeModel('gemini-flash-latest', system_instruction=system_instruction)
        except Exception:
            model = genai.GenerativeModel('gemini-2.0-flash', system_instruction=system_instruction)
        model_initialized = True
    except Exception as e:
        gemini_config_error = str(e)
        st.error(f"Error al configurar Gemini: {e}")

# INTERFAZ PRINCIPAL - CABECERA
with st.container(border=True):
    col_logo, col_titles = st.columns([1, 4], vertical_alignment="center")
    with col_logo:
        # Streamlit renderiza :material:...: solo en texto Markdown normal, no dentro de HTML crudo.
        st.markdown("<h1 style='text-align: center; color: #0077C8; font-size: 4rem; margin:0;'>👷‍♂️</h1>", unsafe_allow_html=True)
    with col_titles:
        st.markdown("<div class='main-title'>INSPECTAPP</div>", unsafe_allow_html=True)
        st.markdown("<div class='main-subtitle'>Tu copiloto digital de inspección</div>", unsafe_allow_html=True)

# TARJETA DE CONFIGURACIÓN DE OBRA (Antes en el Sidebar)
with st.container(border=True):
    st.subheader(":material/engineering: Configuración de Obra")
    col_cfg1, col_cfg2, col_cfg3 = st.columns(3)
    with col_cfg1:
        obra_seleccionada = st.selectbox("Estación / Tramo", ["Medanito", "Allen", "Crucero Catriel", "Puerto Rosales"])
    with col_cfg2:
        inspector = st.text_input("Inspector Oldelval", "Sofi (Ingeniería)")
    with col_cfg3:
        solicitante_contratista = st.text_input("Solicitante Contratista", "Ing. Pedro Gómez")

# FORMULARIO DE DOBLE VERIFICACIÓN EN PESTAÑAS
tab1, tab2 = st.tabs(["🏛️ MOMENTO 1: Gabinete", "🚜 MOMENTO 2: Frente de Obra"])

with tab1:
    with st.container(border=True):
        st.subheader(":material/assignment: 1.1 Verificación Documental")
        col_doc1, col_doc2 = st.columns(2)
        with col_doc1:
            num_permiso = st.text_input("N° Permiso (Sertronic)", "PT-2026-8942")
        with col_doc2:
            num_cpt = st.text_input("N° CPT Asociado (Blister)", "CPT-4402")

        st.write("**Consulta Automatizada de Habilitaciones (Sertronic + Blister):**")
        st.caption("Simulación de la consulta en background a Sertronic (seguros, operarios, maquinaria) y Blister (checklists) prevista en el MVP.")
        resultado_habilitacion = st.radio(
            "Resultado simulado de la consulta",
            [
                "✅ Vigente: seguros, operarios y maquinaria habilitados",
                "🛑 Desvío detectado: documentación vencida o faltante",
            ],
            label_visibility="collapsed",
            key="resultado_habilitacion",
        )
        bloqueo_habilitacion = resultado_habilitacion.startswith("🛑")
        if bloqueo_habilitacion:
            st.error(
                "🛑 BLOQUEO DE SEGURIDAD (HARD GATE)\n\n"
                "Desvío documental detectado en Sertronic/Blister: no se puede abrir el permiso "
                "hasta regularizar la habilitación de la contratista, operarios o maquinaria.",
                icon=":material/block:",
            )
        else:
            st.success("Habilitaciones vigentes. Contratista, operarios y maquinaria en regla.", icon=":material/check_circle:")

    with st.container(border=True):
        st.subheader(":material/gas_meter: 1.2 Control Crítico de Gases")
        col_g1, col_g2, col_g3, col_g4 = st.columns(4)
        with col_g1:
            g_lel = st.number_input("L.E.L (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
        with col_g2:
            g_o2 = st.number_input("O2 (%)", min_value=0.0, max_value=100.0, value=20.9, step=0.1)
        with col_g3:
            g_co = st.number_input("CO (ppm)", min_value=0.0, max_value=1000.0, value=0.0, step=1.0)
        with col_g4:
            g_h2s = st.number_input("H2S (ppm)", min_value=0.0, max_value=500.0, value=0.0, step=1.0)
            
        # LÓGICA HARD GATE
        bloqueo_gases = False
        gases_err = []
        if g_lel > 0.0:
            bloqueo_gases = True
            gases_err.append(f"L.E.L. es {g_lel}% (Debe ser 0%).")
        if g_o2 < 19.5 or g_o2 > 23.5:
            bloqueo_gases = True
            gases_err.append(f"Oxígeno anormal: {g_o2}% (19.5% - 23.5%).")
        if g_co > 25.0:
            bloqueo_gases = True
            gases_err.append(f"CO excedido: {g_co} ppm (Máx 25 ppm).")
        if g_h2s > 10.0:
            bloqueo_gases = True
            gases_err.append(f"H2S tóxico: {g_h2s} ppm (Máx 10 ppm).")
            
        if bloqueo_gases:
            st.error("🛑 BLOQUEO DE SEGURIDAD (HARD GATE)\n\n" + "\n\n".join(gases_err), icon=":material/block:")
        else:
            st.success("Atmósfera segura. Valores dentro del rango tolerado.", icon=":material/check_circle:")
    
    with st.container(border=True):
        st.subheader(":material/draw: 1.3 Firmas CPT")
        cpt_checked = st.checkbox("Certifico bajo declaración jurada haber brindado la charla CPT y verificar firmas en físico.")
        
        # Evidencia fotográfica de la planilla física (cámara nativa o galería)
        st.write("**Evidencia Requerida:**")
        if st.session_state.foto_cpt is None:
            evidencia_cpt = st.file_uploader(
                "📷 Adjuntar foto de la Planilla CPT firmada (abre cámara o galería en el celular)",
                type=["jpg", "jpeg", "png"],
                key="upload_cpt"
            )
            if evidencia_cpt is not None:
                st.session_state.foto_cpt = evidencia_cpt
                st.rerun()
        else:
            st.image(st.session_state.foto_cpt, width=150, caption="Captura CPT")
            if st.button("❌ Eliminar / Volver a adjuntar", key="btn_retake_cpt"):
                st.session_state.foto_cpt = None
                st.rerun()

        col_sig1, col_sig2 = st.columns(2)
        with col_sig1:
            firma_ins = st.checkbox(f"Firma: {inspector} (Oldelval)", disabled=bloqueo_gases or bloqueo_habilitacion or not cpt_checked or st.session_state.foto_cpt is None)
        with col_sig2:
            firma_sol = st.checkbox(f"Firma: {solicitante_contratista} (Contratista)", disabled=bloqueo_gases or bloqueo_habilitacion or not cpt_checked or st.session_state.foto_cpt is None)

        m1_listo = firma_ins and firma_sol and not bloqueo_gases and not bloqueo_habilitacion and st.session_state.foto_cpt is not None
        if m1_listo:
            st.success("Momento 1 completado. Proceder al Momento 2.", icon=":material/done_all:")
        else:
            if bloqueo_habilitacion:
                st.warning("No se puede abrir el permiso: desvío documental en Sertronic/Blister.", icon=":material/gpp_bad:")
            if st.session_state.foto_cpt is None:
                st.warning("Falta captura fotográfica del documento firmado.", icon=":material/photo_camera:")
            st.warning("Complete las validaciones para avanzar.", icon=":material/warning:")

with tab2:
    if not m1_listo:
        st.error("🛑 Momento 2 Bloqueado: Complete el Momento 1 antes de descender al frente de obra.", icon=":material/lock:")
    else:
        with st.container(border=True):
            st.subheader(":material/radar: 2.1 Equipamiento e Entorno")
            col_eq1, col_eq2 = st.columns(2)
            with col_eq1:
                eq_georradar = st.checkbox("Planos georradar en carpeta")
                eq_rd7000 = st.checkbox("RD7000 con calibración vigente")
                eq_acopio = st.checkbox("Acopio de material a > 2.00m del borde")
                eq_clima = st.checkbox("Estabilidad del suelo verificada (sin lluvias)")
            with col_eq2:
                eq_estacado = st.checkbox("Estacas cada 50m (recta) / 10m (curva)")
                cateo_360 = st.checkbox("Cateo manual a 360° (> 1m de ancho)")
                eq_carteles = st.checkbox("Carteles reflectantes a 200m instalados")
        
        with st.container(border=True):
            st.subheader(":material/calculate: 2.2 Tapada Real")
            st.latex(r"T = D_{medida} - R_{cañeria}")
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                d_medida = st.number_input("RD7000 (D_medida en m)", min_value=0.0, value=1.5, step=0.01)
            with col_m2:
                radio_tub = st.number_input("Radio exterior (R_cañería en m)", min_value=0.0, value=0.25, step=0.01)
            st.info(f"📏 **Tapada Real Calculada (T): {d_medida - radio_tub:.2f} metros**", icon=":material/straighten:")
            
        with st.container(border=True):
            st.subheader(":material/warning: 2.3 Zanja Profunda")
            prof_plan = st.number_input("Profundidad de excavación planificada (m)", min_value=0.0, value=1.0, step=0.1)
            
            bloqueo_fosa = False
            fosa_err = []
            
            if prof_plan > 1.20:
                st.warning("⚠️ PROFUNDIDAD CRÍTICA (> 1.20m). Controles obligatorios:", icon=":material/warning:")
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    chk_enti = st.checkbox("Entibados instalados")
                    chk_vigia = st.checkbox("Vigía de Retén en exterior")
                with col_f2:
                    chk_escape = st.checkbox("Doble Salida de Escape (< 8m)")
                    chk_no_madera = st.checkbox("Vallas perimetrales sin madera")
                if not (chk_enti and chk_vigia and chk_escape and chk_no_madera):
                    bloqueo_fosa = True
                    fosa_err.append("Faltan controles SRT 503/14 (> 1.20 m).")
                    
                if prof_plan > 1.50:
                    st.warning("🚧 VALLADO OBLIGATORIO (> 1.50m).", icon=":material/fence:")
                    chk_vallas = st.checkbox("Vallas a mínimo 1.00m del borde")
                    if not chk_vallas:
                        bloqueo_fosa = True
                        fosa_err.append("Falta vallado perimetral a 1.00m.")

                if prof_plan > 1.80:
                    st.error("🚨 MÁXIMO RIESGO (> 1.80m).", icon=":material/personal_injury:")
                    chk_arnes = st.checkbox("Uso de arnés y cabo de vida certificado")
                    if not chk_arnes:
                        bloqueo_fosa = True
                        fosa_err.append("Falta arnés obligatorio.")
            else:
                st.success("Profundidad estándar (< 1.20 m).", icon=":material/check:")
                
            if bloqueo_fosa:
                st.error("🛑 BLOQUEO DE FOSA\n\n" + "\n\n".join(fosa_err), icon=":material/block:")
                
        with st.container(border=True):
            st.subheader(":material/agriculture: 2.4 Posicionamiento de Maquinaria")
            maquinaria_paralela = st.checkbox("Retroexcavadora paralela al ducto")
            excavacion_proxima = st.radio("¿Excavación a menos de 1.00 metro?", ["No (Stop Mecánico)", "Sí (Bypass Crítico)"])
            
            bloqueo_maq = False
            if excavacion_proxima == "Sí (Bypass Crítico)":
                st.error("🚨 DESVÍO CRÍTICO: Vulneración de Stop Mecánico.", icon=":material/warning:")
                metodo = st.selectbox("Aprobación:", ["Código de Supervisor", "Reporte Fotográfico"])
                if metodo == "Código de Supervisor":
                    if st.text_input("Código (1234)", type="password") != "1234":
                        bloqueo_maq = True
                        st.error("❌ Código inválido.")
                    else:
                        st.success("🔓 Bypass autorizado.")
                else:
                    st.write("**Evidencia Requerida:**")
                    if st.session_state.foto_cateo is None:
                        evidencia_cateo = st.file_uploader(
                            "📷 Adjuntar foto del cateo manual a 360° en terreno (abre cámara o galería en el celular)",
                            type=["jpg", "jpeg", "png"],
                            key="upload_cateo"
                        )
                        if evidencia_cateo is not None:
                            st.session_state.foto_cateo = evidencia_cateo
                            st.rerun()
                    else:
                        st.image(st.session_state.foto_cateo, width=150, caption="Captura Cateo 360°")
                        if st.button("❌ Eliminar / Volver a adjuntar", key="btn_retake_cateo"):
                            st.session_state.foto_cateo = None
                            st.rerun()

                    if st.session_state.foto_cateo is None:
                        bloqueo_maq = True
                        st.warning("📸 Faltan evidencias. Es obligatorio adjuntar la foto del cateo.")
                    else:
                        st.success("✅ Evidencia cargada.")
                        
        m2_listo = eq_georradar and eq_rd7000 and eq_estacado and cateo_360 and eq_acopio and eq_clima and eq_carteles and maquinaria_paralela and not bloqueo_fosa and not bloqueo_maq
        
        with st.container(border=True):
            if m2_listo:
                st.balloons()
                st.success("🚀 **¡EXCAVACIÓN AUTORIZADA!**", icon=":material/verified:")
                if st.button("📥 Generar Reporte de Liberación", type="primary"):
                    st.success("📄 Reporte consolidado exportado exitosamente.")
            else:
                st.warning("⚠️ Resuelva los bloqueos para habilitar la excavación.", icon=":material/front_hand:")

# === POPUP CHATBOT FLOTANTE (FAB) ===
# Se inyecta en el main de la app, el CSS previamente definido se encargará de posicionarlo fijo al inferior derecho
with st.popover(" ", width="stretch"):
    col_av1, col_av2 = st.columns([1, 3], vertical_alignment="center")
    with col_av1:
        if os.path.exists("./IVO.png"):
            st.image("./IVO.png", width=65)
        else:
            st.markdown("🤖")
    with col_av2:
        st.markdown("**Ivo ─ Copiloto**")
        st.caption("Asistente técnico Oldelval")
        if not model_initialized:
            st.caption("⚠️ Sin GEMINI_API_KEY configurada — modo simulación")

    if st.session_state.messages:
        if st.button("🗑️ Limpiar", key="clear_chat_btn"):
            st.session_state.messages = []
            st.rerun()

    if not st.session_state.messages:
        SUGGESTIONS = {
            "📏 Tapada": "¿Cómo calculo la tapada real?",
            "🔥 Gases": "¿Valores permisibles de gases?",
            "🚜 Stop Mecánico": "¿Reglas para excavar a menos de 1 metro?"
        }
        selected = st.pills("Sugerencias:", list(SUGGESTIONS.keys()), label_visibility="collapsed")
        if selected:
            st.session_state.messages.append({"role": "user", "content": SUGGESTIONS[selected]})
            st.rerun()

    chat_box = st.container(height=400, border=True)
    with chat_box:
        if not st.session_state.messages:
            st.markdown("👋 **¡Hola! Soy Ivo.** Tu copiloto digital de bolsillo.\n\nPreguntame sobre normativas, LERs o procedimientos.")
        else:
            for message in st.session_state.messages:
                av = "./IVO.png" if (message["role"] == "assistant" and os.path.exists("./IVO.png")) else ("🤖" if message["role"] == "assistant" else "👷‍♂️")
                with st.chat_message(message["role"], avatar=av):
                    st.markdown(message["content"])

            if st.session_state.messages[-1]["role"] == "user":
                av_assistant = "./IVO.png" if os.path.exists("./IVO.png") else "🤖"
                with st.chat_message("assistant", avatar=av_assistant):
                    with st.spinner("Ivo está pensando..."):
                        if model_initialized:
                            try:
                                chat_context = []
                                for msg in st.session_state.messages:
                                    role_name = "user" if msg["role"] == "user" else "model"
                                    chat_context.append({"role": role_name, "parts": [msg["content"]]})
                                response = model.generate_content(chat_context)
                                response_text = response.text
                            except Exception as e:
                                response_text = f"No pude conectarme con Gemini API. Detalle técnico: {str(e)}"
                        else:
                            response_text = (
                                "⚠️ **Modo Simulación:** No se encontró una `GEMINI_API_KEY` válida "
                                "(configúrala en `.streamlit/secrets.toml` o como variable de entorno). "
                                f"{'Detalle: ' + gemini_config_error if gemini_config_error else ''}\n\n"
                                "Ejemplo de respuesta real: La tapada es T = D_medida - R_cañería."
                            )
                        st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                st.rerun()

    if prompt := st.chat_input("Pregúntale a Ivo..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()
