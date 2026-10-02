"""Servicio de validación de cookies."""


from ..config import get_cookies_file


def validate_cookies_file() -> tuple[bool, int, str]:
    """
    Valida el archivo cookies.txt.
    
    Returns:
        tuple: (existe, cantidad_cookies, mensaje)
    """
    cookies_file = get_cookies_file()

    if not cookies_file.exists():
        return False, 0, "cookies.txt NO encontrado"

    try:
        content = cookies_file.read_text(encoding="utf-8", errors="ignore")
        lines = content.strip().split("\n")
        cookie_lines = [l for l in lines if l and not l.startswith("#")]
        count = len(cookie_lines)

        if count == 0:
            return True, 0, "cookies.txt existe pero esta vacio (sin cookies validas)"

        return True, count, f"cookies.txt valido ({count} cookies)"
    except Exception as e:
        return False, 0, f"Error leyendo cookies.txt: {e}"


def get_cookies_status_message() -> str:
    """Retorna mensaje de estado para UI."""
    existe, count, msg = validate_cookies_file()
    if existe:
        return f"[green]{msg}[/green]"
    return f"[red]{msg}[/red]"