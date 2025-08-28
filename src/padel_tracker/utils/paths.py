from pathlib import Path
import re
import unicodedata


def get_absolute_path(current_file: str | Path, rel_path: str | Path) -> Path:
    """
    Get an absolute path of a relative position from current module/package

    Examples
    --------
    # To be called like this :

    >>> conf_file = get_absolute_path(__file__, "../../../data/config.toml")

    Parameters
    ----------
    current_file: str|Path
        Must be __file__
    rel_path: str|Path
        The relative path wanted

    Returns
    -------
    abs_path : Path
        Resolved absolute path from relative "rel_path"
    """
    return (Path(current_file).parent / Path(rel_path)).resolve()


def sanitize_filename(name: str, replacement: str = "_") -> str:
    # Normalize accents (é -> e, ç -> c, etc.)
    normalized = unicodedata.normalize("NFKD", name)
    normalized = normalized.encode("ascii", "ignore").decode("ascii")
    # Remove any character not in this set: letters, numbers, dash, underscore, dot, space
    sanitized = re.sub(r"[^A-Za-z0-9._ -]", replacement, normalized)
    # Collapse multiple replacements (___ -> _)
    sanitized = re.sub(rf"{re.escape(replacement)}+", replacement, sanitized)
    # Strip leading/trailing spaces, dots, or underscores (Windows hates trailing dots/spaces)
    sanitized = sanitized.strip(" ._")

    return sanitized or "untitled"


APP_PATH = get_absolute_path(__file__, "../ui/streamlit_app.py")
