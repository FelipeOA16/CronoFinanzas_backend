from typing import List, Any


def get_cors_origins(raw: Any) -> List[str]:
    if raw == "*":
        return ["*"]
    if isinstance(raw, list):
        return raw
    return raw or []
