# secret_context.py

_secret_mapping_singleton: dict = {}

def set_secret_mapping(mapping: dict):
    global _secret_mapping_singleton
    _secret_mapping_singleton = mapping

def get_secret_mapping() -> dict:
    return _secret_mapping_singleton
