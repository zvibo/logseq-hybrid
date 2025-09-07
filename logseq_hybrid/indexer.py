from __future__ import annotations
from pathlib import Path
from typing import Dict, List
from .settings import PAGES_DIR, JOURNALS_DIR

def list_pages() -> List[str]:
    return sorted([p.stem for p in PAGES_DIR.glob("*.md")])

def list_journals() -> List[str]:
    return sorted([p.stem for p in JOURNALS_DIR.glob("*.md")])

def read_page(name: str) -> str:
    p = PAGES_DIR / (name if name.endswith(".md") else name + ".md")
    return p.read_text(encoding="utf-8") if p.exists() else ""

def grep(term: str) -> Dict[str, int]:
    """Very simple content grep across pages; returns counts per file."""
    term_lower = term.lower()
    hits: Dict[str, int] = {}
    for p in list(PAGES_DIR.glob("*.md")) + list(JOURNALS_DIR.glob("*.md")):
        txt = p.read_text(encoding="utf-8")
        c = txt.lower().count(term_lower)
        if c:
            hits[p.name] = c
    return dict(sorted(hits.items(), key=lambda kv: kv[1], reverse=True))
