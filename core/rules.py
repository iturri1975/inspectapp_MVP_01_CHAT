"""Reglas de negocio (Hard Gates) como funciones puras, reutilizables entre pantallas."""


def evaluar_gases(lel: float, o2: float, co: float, h2s: float):
    """Devuelve (bloqueado: bool, errores: list[str]) según los umbrales normativos de Oldelval."""
    errores = []
    if lel > 0.0:
        errores.append(f"L.E.L. es {lel}% (Debe ser 0%).")
    if o2 < 19.5 or o2 > 23.5:
        errores.append(f"Oxígeno anormal: {o2}% (19.5% - 23.5%).")
    if co > 25.0:
        errores.append(f"CO excedido: {co} ppm (Máx 25 ppm).")
    if h2s > 10.0:
        errores.append(f"H2S tóxico: {h2s} ppm (Máx 10 ppm).")
    return (len(errores) > 0, errores)


def evaluar_zanja(prof_plan: float, chk_vigia: bool, chk_escape: bool, chk_no_madera: bool,
                   entibado_aplica, chk_entibado_instalado: bool,
                   chk_vallas: bool, chk_arnes: bool):
    """Devuelve (bloqueado: bool, errores: list[str]) para los controles de zanja profunda.

    entibado_aplica: "Sí" | "No" | None. Si es "Sí" y no está instalado, bloquea.
    Si es None (sin definir), también bloquea: el inspector debe consultar la
    tipificación de suelos antes de poder avanzar.
    """
    if prof_plan <= 1.20:
        return (False, [])

    errores = []
    if not (chk_vigia and chk_escape and chk_no_madera):
        errores.append("Faltan controles obligatorios (> 1.20 m): vigía de retén, doble salida de escape o vallas sin madera.")

    if entibado_aplica is None:
        errores.append("Definí si el entibado aplica (consultá la tipificación de suelos) antes de continuar.")
    elif entibado_aplica == "Sí" and not chk_entibado_instalado:
        errores.append("El entibado aplica según el tipo de suelo y todavía no está instalado.")

    if prof_plan > 1.50 and not chk_vallas:
        errores.append("Falta vallado perimetral a 1.00 m del borde (obligatorio > 1.50 m).")

    if prof_plan > 1.80 and not chk_arnes:
        errores.append("Falta arnés de cuerpo completo y cabo de vida (obligatorio > 1.80 m).")

    return (len(errores) > 0, errores)


def evaluar_sertronic(personal: str, vehiculos: str, maquinaria: str):
    """Devuelve (bloqueado: bool, detalle: dict) según el mock binario Verde/Rojo por recurso."""
    detalle = {"Personal": personal, "Vehículos": vehiculos, "Maquinaria": maquinaria}
    bloqueado = any(v == "Rojo" for v in detalle.values())
    return (bloqueado, detalle)
