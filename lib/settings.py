import json
from pathlib import Path

SETTINGS_PATH = Path(__file__).parent.parent / 'settings.json'

DEFAULT_SETTINGS = {
    "ignoreClipboardOverwritingWarning": False,
}


def _load():
    if not SETTINGS_PATH.exists():
        _save(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()
    try:
        with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError('settings file is not a JSON object')
        return data
    except Exception:
        _save(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()


def _save(data):
    with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent='\t')


def set(id: str, context):
    s = _load()
    s[id] = context
    _save(s)


def get(id: str, default=None):
    s = _load()
    return s[id] if id in s else default


def js():
    return _load()
