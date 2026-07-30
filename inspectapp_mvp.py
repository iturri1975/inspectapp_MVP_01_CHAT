import streamlit as st
import google.generativeai as genai
import pandas as pd

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="INSPECTAPP MVP v4.0",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ESTILOS CSS PERSONALIZADOS PARA ADAPTACIÓN MÓVIL Y DISEÑO OLDELVAL
st.markdown("""
<style>
    /* Estilos del header principal */
    .main-title {
        color: #0077C8;
        font-family: 'Roboto', sans-serif;
        font-weight: 700;
        font-size: 2.2rem;
        margin-bottom: 5px;
    }
    .main-subtitle {
        color: #555555;
        font-family: 'Roboto', sans-serif;
        font-weight: 400;
        font-size: 1.1rem;
        margin-bottom: 25px;
    }
    /* Estilos de los paneles de Momentos */
    .momento-card {
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        border-left: 5px solid #0077C8;
        background-color: #F8F9FA;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .momento-title {
        font-size: 1.25rem;
        font-weight: bold;
        color: #0077C8;
        margin-bottom: 10px;
    }
    /* Panel de alerta Hard Gate */
    .hard-gate-alert {
        background-color: #FFEBEB;
        border-left: 5px solid #D9381E;
        padding: 12px;
        border-radius: 4px;
        color: #D9381E;
        font-weight: bold;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# INICIALIZACIÓN DEL CHATBOT DE GEMINI
if "messages" not in st.session_state:
    st.session_state.messages = []

# Configuración del modelo Gemini utilizando st.secrets para producción segura
api_key = st.secrets.get("GEMINI_API_KEY", None)
model_initialized = False

if api_key:
    try:
        genai.configure(api_key=api_key)
        # Instrucción de sistema ultra-detallada (System Prompt) para adiestrar a Ivo
        system_instruction = (
            "Eres Ivo, el Co-piloto Digital Inteligente de INSPECTAPP para los inspectores de campo de Oldelval.\n"
            "Tu objetivo es brindar soporte técnico en tiempo real, resolver dudas sobre procedimientos y ayudar en la toma de decisiones antes y durante la inspección.\n"
            "Sé profesional, conciso, de habla hispana, extremadamente riguroso con la seguridad operacional y amigable.\n\n"
            "Reglas técnicas críticas de Oldelval que debes conocer de memoria y exigir cuando te consulten:\n"
            "1. Fórmula de Tapada Real (IT_OL_PDD_04): T = D_medida - R_cañería. Donde D_medida es la profundidad al eje leída por el detector RD7000, y R_cañería es el radio exterior del caño. El inspector debe marcar T en la estaca.\n"
            "2. Gases y Habilitación de AT en Caliente (PO_OL_EIR_03):\n"
            "   - L.E.L. (Gases Inflamables): Debe ser 0% absoluto para iniciar tareas.\n"
            "   - Oxígeno (O2): Debe estar entre 19.5% y 23.5%.\n"
            "   - Monóxido de Carbono (CO): Máximo 25 ppm.\n"
            "   - Ácido Sulfhídrico (H2S): Máximo 10 ppm.\n"
            "   Si se supera cualquiera de estos valores, se bloquea la habilitación de firmas y tareas.\n"
            "3. Código de Colores de Estacado (IT_OL_PDD_04):\n"
            "   - Parte superior Negra, cuerpo Amarillo: Instalación a descubrir/intervenir con excavación mecánica posterior.\n"
            "   - Parte superior Roja, cuerpo Blanco: Interferencia o cruce (excavación mecánica bloqueada a menos de 1m).\n"
            "   - Blanco absoluto: Instalaciones paralelas (referencia de proximidad, nunca se excava).\n"
            "4. Excavaciones y Zanja Profunda (PO_OL_EIR_08 / SRT 503/14):\n"
            "   - Si profundidad > 1.20 metros: Es umbral crítico. Requiere entibados/apuntalamientos instalados desde el exterior, Vigía de Retén permanente afuera con equipo autónomo, y Doble Salida de Escape independiente por extremo (escalera/rampa a cada lado del caño en sus extremos, distancia máxima de traslado < 8m). Prohibido usar madera como vallas o vallados rígidos.\n"
            "   - Si profundidad > 1.80 metros: Requisito de máximo riesgo. Obligatorio arnés de seguridad de cuerpo completo y cabo de vida amarrado a punto fijo exterior certificado.\n"
            "5. Maquinaria y Excavación Mecánica:\n"
            "   - La retroexcavadora debe operar con la herramienta paralela al ducto y el operador con visión 100% libre (o señalero a distancia mayor al diámetro de trabajo).\n"
            "   - Stop Mecánico estricto a 1.00 metro de distancia del caño. Para excavar a menos de 1.00m, se requiere bypass con aprobación excepcional (código 1234) o reporte de desvío con fotos.\n"
            "   - Excavación mecánica requiere previamente cateo manual a 360° con ancho de 1m a cada lado del ducto.\n\n"
            "Cuando te pregunten sobre qué tareas hacer para una actividad del día (ej. 'pintar el techo'):\n"
            "- Identifica qué riesgos aplican (ej. andamios, trabajos en altura) y qué checklist o LER disparar (ej. LER Trabajo en Altura, uso de arnés, mentonera en casco si hay viento).\n"
            "Responde de forma natural y conversacional, priorizando siempre la seguridad física de los operarios."
        )
        model = genai.GenerativeModel('gemini-1.5-pro', system_instruction=system_instruction)
        model_initialized = True
    except Exception as e:
        st.error(f"Error al configurar Gemini: {e}")

# INTERFAZ PRINCIPAL - CABECERA
st.markdown("<div class='main-title'>INSPECTAPP v4.0</div>", unsafe_allow_html=True)
st.markdown("<div class='main-subtitle'>El Copiloto Digital del Inspector en Campo ─ Versión de Validación de Arquitectura</div>", unsafe_allow_html=True)

# BARRA LATERAL CON CHATBOT FLOTANTE Y PARÁMETROS GENERALES
with st.sidebar:
    # Logo de la empresa
    st.image("https://www.oldelval.com/wp-content/uploads/2021/04/Logo-Oldelval-min.png", width=180, output_format="PNG")
    st.markdown("---")
    
    # SECCIÓN DEL CHATBOT DE IVO CON POPOVER FLOTANTE (Ideal para UX móvil)
    st.subheader("🤖 Asistente Técnico Ivo")
    with st.popover("💬 Hablar con Ivo (Co-piloto)", use_container_width=True):
        st.markdown("**¡Hola! Soy Ivo.** 🦾 Tu copiloto digital de bolsillo.")
        st.write("Preguntame cualquier regla técnica (como la fórmula de tapada, colores de estacas o gases) o contame qué tareas vas a realizar hoy para ayudarte con el pre-checklist.")
        
        # Mostrar el historial de mensajes
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
        # Input de chat
        if prompt := st.chat_input("Escribile a Ivo..."):
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Obtener respuesta utilizando la API Real de Gemini
            if model_initialized:
                try:
                    chat_context = []
                    for msg in st.session_state.messages:
                        role_name = "user" if msg["role"] == "user" else "model"
                        chat_context.append({"role": role_name, "parts": [msg["content"]]})
                    
                    response = model.generate_content(chat_context)
                    response_text = response.text
                except Exception as ex:
                    response_text = f"Ups, no pude conectarme con mi cerebro de IA: {ex}. Pero recordá que para excavaciones mayores a 1.20m necesitás doble salida de escape y vigía."
            else:
                # Simulación por si aún no configuraste la variable en Streamlit Cloud
                response_text = (
                    "⚠️ **Nota de Desarrollo:** No se detectó la variable `GEMINI_API_KEY` en los Secrets de Streamlit.\n\n"
                    "**Respuesta Simulación de Ivo:** ¡Hola! Como copiloto interactivo de Oldelval, te recuerdo que la fórmula de tapada real es `T = D_medida - R_cañería`. "
                    "Si hoy tenés que *pintar un techo*, recordá que al superar el 1.50m de altura debés exigir el arnés completo con cabo de vida y el checklist de Trabajo en Altura."
                )
            
            with st.chat_message("assistant"):
                st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})

    st.markdown("---")
    st.subheader("Configuración de Obra")
    obra_seleccionada = st.selectbox("Estación de Bombeo / Tramo", ["Medanito", "Allen", "Crucero Catriel", "Puerto Rosales"])
    inspector = st.text_input("Inspector a cargo", "Sofi (Ingeniería)")
    solicitante_contratista = st.text_input("Solicitante Contratista", "Ing. Pedro Gómez")

st.info("💡 **Objetivo de esta V1:** Validar arquitectura, flujo de toma de decisiones y el comportamiento del copiloto interactivo (incluyendo a Ivo) antes de la prueba piloto con los inspectores de campo.")

# FORMULARIO DE DOBLE VERIFICACIÓN
tab1, tab2 = st.tabs(["🏛️ MOMENTO 1: Apertura de Permiso (Gabinete)", "🚜 MOMENTO 2: Habilitación en Frente de Obra"])

with tab1:
    st.markdown("<div class='momento-card'>", unsafe_allow_html=True)
    st.markdown("<div class='momento-title'>1.1 Verificación Documental (Sertronic y Blister)</div>", unsafe_allow_html=True)
    num_permiso = st.text_input("N° de Permiso de Trabajo (Sertronic)", "PT-2026-8942")
    num_cpt = st.text_input("N° de CPT Asociado (Blister)", "CPT-4402")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='momento-card'>", unsafe_allow_html=True)
    st.markdown("<div class='momento-title'>1.2 Control Crítico de Gases (Analista de Gases)</div>", unsafe_allow_html=True)
    st.write("Registre las mediciones atmosféricas obligatorias para habilitar el permiso de trabajo:")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        g_lel = st.number_input("Gases Inflamables (L.E.L %)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
    with col2:
        g_o2 = st.number_input("Oxígeno (O2 %)", min_value=0.0, max_value=100.0, value=20.9, step=0.1)
    with col3:
        g_co = st.number_input("Monóxido Carbono (CO ppm)", min_value=0.0, max_value=1000.0, value=0.0, step=1.0)
    with col4:
        g_h2s = st.number_input("Ácido Sulfhídrico (H2S ppm)", min_value=0.0, max_value=500.0, value=0.0, step=1.0)
        
    # LOGICA HARD GATE DE GASES
    bloqueo_gases = False
    gases_err = []
    
    if g_lel > 0.0:
        bloqueo_gases = True
        gases_err.append(f"Presencia de gases inflamables: L.E.L. es {g_lel}% (Debe ser 0% absoluto para habilitar firmas).")
    if g_o2 < 19.5 or g_o2 > 23.5:
        bloqueo_gases = True
        gases_err.append(f"Oxígeno fuera de rango seguro: {g_o2}% (Debe estar entre 19.5% y 23.5%).")
    if g_co > 25.0:
        bloqueo_gases = True
        gases_err.append(f"Monóxido de Carbono excedido: {g_co} ppm (Máximo permitido: 25 ppm).")
    if g_h2s > 10.0:
        bloqueo_gases = True
        gases_err.append(f"Ácido Sulfhídrico tóxico detectado: {g_h2s} ppm (Máximo permitido: 10 ppm).")
        
    if bloqueo_gases:
        st.markdown("<div class='hard-gate-alert'>🛑 BLOQUEO ABSOLUTO DE SEGURIDAD (HARD GATE)<br/>" + 
                    "<br/>".join(gases_err) + "</div>", unsafe_allow_html=True)
    else:
        st.success("✅ Atmósfera segura. Valores dentro de los rangos tolerados por Oldelval.")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='momento-card'>", unsafe_allow_html=True)
    st.markdown("<div class='momento-title'>1.3 CPT Simplificado (Firma de Cuadrilla - Opción B)</div>", unsafe_allow_html=True)
    st.write("Para agilizar el trámite, el inspector certifica que la cuadrilla completa firmó la planilla física de obra en papel.")
    
    cpt_checked = st.checkbox("Certifico bajo declaración jurada haber brindado la charla de seguridad (CPT) de 10 minutos al frente de obra, repasando los riesgos críticos identificados en la matriz IPER/IAEI y verificando las firmas en el soporte físico correspondiente.")
    
    col_sig1, col_sig2 = st.columns(2)
    with col_sig1:
        firma_ins = st.checkbox(f"Firma digital: {inspector} (Inspector Oldelval)", disabled=bloqueo_gases or not cpt_checked)
    with col_sig2:
        firma_sol = st.checkbox(f"Firma digital: {solicitante_contratista} (Solicitante Contratista)", disabled=bloqueo_gases or not cpt_checked)
        
    m1_listo = firma_ins and firma_sol and not bloqueo_gases
    if m1_listo:
        st.success("🎉 Momento 1 Habilitado y Firmado. Puede proceder al Momento 2 en el Frente de Obra.")
    else:
        st.warning("⚠️ Complete todas las firmas y validaciones sin desvíos para poder avanzar.")
    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    if not m1_listo:
        st.error("🛑 Momento 2 Bloqueado: Debe completar y firmar la apertura documental en el Momento 1 (Gabinete) antes de descender al frente de excavación.")
    else:
        st.markdown("<div class='momento-card'>", unsafe_allow_html=True)
        st.markdown("<div class='momento-title'>2.1 Auditoría de Equipamiento e Interferencias en Sitio</div>", unsafe_allow_html=True)
        col_eq1, col_eq2 = st.columns(2)
        with col_eq1:
            eq_georradar = st.checkbox("¿Se cuenta físicamente con los planos de georradar impresos en la carpeta de obra?")
            eq_rd7000 = st.checkbox("¿El detector electromagnético RD7000 posee certificado de calibración vigente?")
        with col_eq2:
            eq_estacado = st.checkbox("¿Se instalaron estacas de eje cada 50 metros en rectas y cada 10 metros en curvas?")
            cateo_360 = st.checkbox("¿Se realizó el cateo manual a 360° con un ancho mínimo de 1 metro a cada lado del ducto?")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='momento-card'>", unsafe_allow_html=True)
        st.markdown("<div class='momento-title'>2.2 Asistente Matemático de Tapada Real (T) (Norma IT_OL_PDD_04)</div>", unsafe_allow_html=True)
        st.write("La app calcula instantáneamente la tapada real del caño aplicando la ecuación matemática reglamentaria para evitar errores de interpretación:")
        st.latex(r"T = D_{medida} - R_{cañeria}")
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            d_medida = st.number_input("Profundidad registrada al eje por RD7000 (D_medida en metros)", min_value=0.0, max_value=10.0, value=1.5, step=0.01)
        with col_m2:
            radio_tub = st.number_input("Radio exterior de la tubería (R_cañería en metros)", min_value=0.0, max_value=2.0, value=0.25, step=0.01)
            
        tapada_real = d_medida - radio_tub
        st.info(f"📏 **Tapada Real Calculada (T): {tapada_real:.2f} metros** (Este valor debe ser rotulado de forma física en la estaca de madera).")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='momento-card'>", unsafe_allow_html=True)
        st.markdown("<div class='momento-title'>2.3 Dinamización por Profundidad (Resolución SRT 503/14 y PO_OL_EIR_08)</div>", unsafe_allow_html=True)
        prof_plan = st.number_input("Profundidad planificada de excavación (metros)", min_value=0.0, max_value=10.0, value=1.0, step=0.1)
        
        bloqueo_fosa = False
        fosa_err = []
        
        if prof_plan > 1.20:
            st.warning(f"⚠️ **PROFUNDIDAD CRÍTICA (> 1.20m):** Se dispara automáticamente la sección especial de Zanja Profunda (SST en fosa).")
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                chk_enti = st.checkbox("Entibados y apuntalamientos instalados de forma segura desde el exterior.")
                chk_vigia = st.checkbox("Presencia constante de un Vigía de Retén en el exterior con equipamiento de emergencia.")
            with col_f2:
                chk_escape = st.checkbox("Doble Salida de Escape independiente: escaleras/rampas a ambos lados del caño (< 8m de traslado).")
                chk_no_madera = st.checkbox("Certifico que NO se utilizó madera como valla o vallado rígido perimetral.")
                
            if not (chk_enti and chk_vigia and chk_escape and chk_no_madera):
                bloqueo_fosa = True
                fosa_err.append("Faltan controles obligatorios de Zanja Profunda (> 1.20 m) exigidos por la Res. SRT 503/14.")
                
            if prof_plan > 1.80:
                st.error("🚨 **ALERTA DE MÁXIMO RIESGO (> 1.80m):** Se exige obligatoriamente el uso de arnés con cabo de vida.")
                chk_arnes = st.checkbox("Operarios en el fondo de fosa sujetos permanentemente con arnés de seguridad y cabo de vida a punto fijo certificado en el exterior.")
                if not chk_arnes:
                    bloqueo_fosa = True
                    fosa_err.append("Falta validación de uso obligatorio de Arnés y Cabo de vida certificado en profundidades superiores a 1.80 m.")
        else:
            st.success("📐 Profundidad estándar (< 1.20 m). No se requieren controles críticos adicionales de fosa.")
            
        if bloqueo_fosa:
            st.markdown("<div class='hard-gate-alert'>🛑 BLOQUEO DE EXCAVACIÓN EN FOSA<br/>" + 
                        "<br/>".join(fosa_err) + "</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='momento-card'>", unsafe_allow_html=True)
        st.markdown("<div class='momento-title'>2.4 Posicionamiento de Maquinaria y Bypass de Desvío</div>", unsafe_allow_html=True)
        st.write("Estándar: Retroexcavadora con herramienta paralela al ducto y Stop Mecánico estricto a 1.00 metro del caño.")
        
        maquinaria_paralela = st.checkbox("¿Se encuentra la retroexcavadora posicionada con la herramienta paralela al ducto?")
        excavacion_proxima = st.radio("¿Se requiere excavación mecánica a menos de 1.00 metro del caño?", ["No (Respetar Stop Mecánico)", "Sí (Bypass de Desvío Crítico)"])
        
        bloqueo_maq = False
        if excavacion_proxima == "Sí (Bypass de Desvío Crítico)":
            st.error("🚨 DESVÍO CRÍTICO DETECTADO: Se vulnera la barrera del Stop Mecánico de 1.00 m.")
            metodo_excepcion = st.selectbox("Método de Aprobación del Desvío:", ["Aprobación Excepcional por Código de Supervisor", "Generar Reporte de Desvío con Registro Fotográfico"])
            
            if metodo_excepcion == "Aprobación Excepcional por Código de Supervisor":
                codigo_sup = st.text_input("Ingrese código numérico remoto de Supervisor para Bypass", type="password")
                if codigo_sup != "1234":
                    bloqueo_maq = True
                    st.error("❌ Código de supervisor inválido o ausente. El arranque de la retroexcavadora sigue bloqueado.")
                else:
                    st.success("🔓 Bypass autorizado de forma remota por el Supervisor.")
            else:
                foto_desvio = st.file_uploader("Subir foto obligatoria del cateo manual expuesto a 360° antes del inicio de excavación mecánica próxima", type=["png", "jpg", "jpeg"])
                if not foto_desvio:
                    bloqueo_maq = True
                    st.warning("📸 Debe subir la evidencia fotográfica del cateo manual a 360° para habilitar el reporte de desvío y enviar la notificación automática al supervisor.")
                else:
                    st.success("✅ Evidencia fotográfica cargada correctamente. Se enviará el reporte automático por email.")
                    
        m2_listo = eq_georradar and eq_rd7000 and eq_estacado and cateo_360 and maquinaria_paralela and not bloqueo_fosa and not bloqueo_maq
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='momento-card'>", unsafe_allow_html=True)
        st.markdown("<div class='momento-title'>2.5 Liberación y Cierre de la Inspección</div>", unsafe_allow_html=True)
        if m2_listo:
            st.balloons()
            st.success("🚀 **¡EXCAVACIÓN AUTORIZADA!** Se han superado todas las barreras físicas y lógicas del Copiloto Digital.")
            st.write("Presione el botón para generar el reporte de liberación y archivar el duplicado en la estación:")
            if st.button("📥 Generar Reporte e Informe de Gestión"):
                st.success("📄 Reporte consolidado exportado a la base de datos de Oldelval. Notificación enviada al supervisor.")
        else:
            st.warning("⚠️ Para liberar la excavación, debe resolver todos los bloqueos lógicos en Zanja Profunda o en el Bypass de Maquinaria.")
        st.markdown("</div>", unsafe_allow_html=True)
