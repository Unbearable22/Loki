import json
from functools import lru_cache
from pathlib import Path

LOCALES_DIR = Path(__file__).resolve().parent.parent / "locales"
DEFAULT_LOCALE = "ru"

@lru_cache
def load_locale(locale: str) -> dict:
    path = LOCALES_DIR / f"{locale}.json"
    if not path.exists():
        path = LOCALES_DIR / f"{DEFAULT_LOCALE}.json"
    return json.loads(path.read_text(encoding="utf-8"))

def t(locale: str, key: str, **kwargs) -> str:
    value = load_locale(locale)
    for part in key.split("."):
        value = value.get(part) if isinstance(value, dict) else None
    if not isinstance(value, str):
        return key
    return value.format(**kwargs)

def available_locales():
    return sorted(p.stem for p in LOCALES_DIR.glob("*.json"))
