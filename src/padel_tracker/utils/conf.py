import tomllib
from typing import Any
from pathlib import Path

from padel_tracker.utils.paths import get_absolute_path

DEFAULT_CONFIG_FILE = get_absolute_path(__file__, "../conf.toml")


def get_conf(filepath: str | Path = DEFAULT_CONFIG_FILE) -> dict[str, Any]:
    if isinstance(filepath, str):
        filepath = Path(filepath)
    if not isinstance(filepath, Path):
        raise TypeError(f"filepath is not correct type. Got {filepath=}")
    with filepath.open(mode="rb") as file:
        conf = tomllib.load(file)
    return conf
