"""Formateo de magnitudes para la interfaz."""

UNIDADES = ("B", "KB", "MB", "GB", "TB")


def formatear_bytes(cantidad: float | None) -> str:
    """Tamano legible: 499555 -> '487.8 KB'. Devuelve '--' si no se sabe."""
    if cantidad is None or cantidad < 0:
        return "--"
    valor = float(cantidad)
    for unidad in UNIDADES:
        if valor < 1024 or unidad == UNIDADES[-1]:
            return f"{int(valor)} B" if unidad == "B" else f"{valor:.1f} {unidad}"
        valor /= 1024
    return f"{valor:.1f} TB"


def formatear_velocidad(bytes_por_segundo: float | None) -> str:
    """Velocidad legible: 1048576 -> '1.0 MB/s'. Vacio si no se sabe."""
    if not bytes_por_segundo or bytes_por_segundo <= 0:
        return ""
    return f"{formatear_bytes(bytes_por_segundo)}/s"


def formatear_eta(segundos: int | None) -> str:
    """Duracion legible: 3725 -> '1:02:05'. Vacio si no se sabe."""
    if segundos is None or segundos < 0:
        return ""
    horas, resto = divmod(int(segundos), 3600)
    minutos, seg = divmod(resto, 60)
    if horas:
        return f"{horas}:{minutos:02d}:{seg:02d}"
    return f"{minutos}:{seg:02d}"
