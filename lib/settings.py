import json
from pathlib import Path

SETTINGS_PATH = Path(__file__).parent.parent / 'settings.json'


def set(id: str, context):
    with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
        s = json.load(f)
    s[id] = context
    with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
        json.dump(s, f, ensure_ascii=False, indent='\t')


def get(id: str):
    with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)[id]


def js():
    with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)
