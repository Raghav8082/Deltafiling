from pathlib import Path

ROOT = Path("data")  

def save_text(key: str, content: str) -> str:
    path = ROOT / key
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return str(path)