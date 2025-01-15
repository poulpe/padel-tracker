from pathlib import Path


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
    if isinstance(current_file, str):
        current_file = Path(current_file)
    if isinstance(rel_path, str):
        rel_path = Path(rel_path)
    return (current_file.parent / rel_path).resolve()
