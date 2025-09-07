from __future__ import annotations
from pathlib import Path
from datetime import datetime
from typing import Optional
from .settings import PAGES_DIR, JOURNALS_DIR, TMP_DIR, JOURNAL_FMT

def _atomic_write(target: Path, data: str) -> None:
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    tmp = TMP_DIR / (target.name + ".tmp")
    tmp.write_text(data, encoding="utf-8")
    tmp.replace(target)

def ensure_page(name: str, initial: str = "") -> Path:
    filename = f"{name}.md" if not name.lower().endswith(".md") else name
    path = PAGES_DIR / filename
    if not path.exists():
        _atomic_write(path, initial)
    return path

def append_to_page(name: str, content: str) -> Path:
    path = ensure_page(name)
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    new = current.rstrip() + "\n\n" + content.strip() + "\n"
    _atomic_write(path, new)
    return path

def append_journal(content: str, date: Optional[datetime] = None) -> Path:
    dt = date or datetime.now()
    fname = dt.strftime(JOURNAL_FMT) + ".md"
    path = JOURNALS_DIR / fname
    header = f"- {dt.strftime('%H:%M')} "
    entry = header + content.strip() + "\n"
    if path.exists():
        current = path.read_text(encoding="utf-8")
        new = current.rstrip() + "\n" + entry
    else:
        new = entry
    _atomic_write(path, new)
    return path
