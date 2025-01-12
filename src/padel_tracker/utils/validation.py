def ensure_frozen_field(self, key: str, frozen_fields: set[str]) -> None:
    """Ensure a field is not 'read-only', raises AttributeError otherwise"""
    try:
        field_exists = self.__getattr__(key) is not None
    except AttributeError:
        field_exists = False
    if (key in frozen_fields) and field_exists:
        raise AttributeError(f"{key} is read-only, cannot be rewritten")
