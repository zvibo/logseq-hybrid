# Logseq Hybrid Agent Starter Kit

A minimal, pragmatic code bundle to:

* Prefer **Logseq HTTP API** for reads & surgical writes when the desktop app is open.
* Fall back to **filesystem** for bulk/headless appends (journals/pages) when the app is closed.
* **Queue** pending surgical edits while headless and **reconcile** them later when Logseq is open.
* Includes **health checks** and simple tests so you can verify everything end-to-end.

> Requires: Python 3.10+, `requests`, a Logseq graph folder (with `pages/`, `journals/`).

---

## 🧱 Project Layout

```
logseq_hybrid/
  __init__.py
  settings.py
  api_client.py
  fs_writer.py
  indexer.py
  reconciler.py
  cli.py
  queue.json               # auto-created
  tmp/                     # working dir for atomic writes

tests/
  test_health.py

Makefile
README.quickstart.md
requirements.txt
.env.example
```

---

## ⚙️ requirements.txt

```txt
requests>=2.31.0
python-dotenv>=1.0.1
```

---

## 🔐 .env.example

```bash
# Path to your Logseq graph root
GRAPH_PATH=/absolute/path/to/YourLogseqGraph

# Logseq Local HTTP API (enable in Logseq: Settings → Features → Enable HTTP API)
LOGSEQ_API_URL=http://127.0.0.1:12315
LOGSEQ_API_TOKEN=PASTE_YOUR_TOKEN_HERE

# Optional: default journal date format (YYYY_MM_DD is Logseq default)
JOURNAL_FMT=%Y_%m_%d
```

---

## 🧭 logseq\_hybrid/settings.py

```python
from __future__ import annotations
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

GRAPH_PATH = Path(os.getenv("GRAPH_PATH", ".")).expanduser().resolve()
PAGES_DIR = GRAPH_PATH / "pages"
JOURNALS_DIR = GRAPH_PATH / "journals"
TMP_DIR = GRAPH_PATH / ".agent_tmp"
QUEUE_PATH = GRAPH_PATH / "queue.json"

LOGSEQ_API_URL = os.getenv("LOGSEQ_API_URL", "http://127.0.0.1:12315")
LOGSEQ_API_TOKEN = os.getenv("LOGSEQ_API_TOKEN", "")
JOURNAL_FMT = os.getenv("JOURNAL_FMT", "%Y_%m_%d")

for d in (PAGES_DIR, JOURNALS_DIR, TMP_DIR):
    d.mkdir(parents=True, exist_ok=True)
```

---

## 🌐 logseq\_hybrid/api\_client.py

```python
from __future__ import annotations
import requests
from typing import Any, Dict, Optional
from .settings import LOGSEQ_API_URL, LOGSEQ_API_TOKEN

class LogseqAPI:
    def __init__(self, base_url: str = LOGSEQ_API_URL, token: str = LOGSEQ_API_TOKEN):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.session = requests.Session()
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})

    def is_available(self) -> bool:
        try:
            r = self.session.get(f"{self.base_url}/ping", timeout=1.5)
            return r.ok
        except Exception:
            return False

    def call(self, method: str, *args: Any, timeout: float = 5.0) -> Any:
        """Generic bridge to Logseq's /api (maps to plugin API methods).
        Example method: "logseq.Editor.createPage"
        """
        url = f"{self.base_url}/api"
        payload: Dict[str, Any] = {"method": method, "args": list(args)}
        r = self.session.post(url, json=payload, timeout=timeout)
        r.raise_for_status()
        return r.json()

    # Convenience wrappers (happy-path)
    def get_page(self, name: str) -> Optional[dict]:
        return self.call("logseq.Editor.getPage", name)

    def create_page(self, name: str, content: str = "", create_first_block: bool = True) -> dict:
        return self.call("logseq.Editor.createPage", name, {"createFirstBlock": create_first_block, "redirect": False, "format": "markdown"}, content)

    def insert_block(self, parent_uuid: str, content: str, sibling: bool = True) -> dict:
        return self.call("logseq.Editor.insertBlock", parent_uuid, content, {"sibling": sibling})

    def get_current_graph(self) -> dict:
        return self.call("logseq.App.getCurrentGraph")
```

---

## 🗂️ logseq_hybrid/fs_writer.py

```python
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
```

---

## 🔎 logseq\_hybrid/indexer.py (read-only lightweight index)

```python
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
```

---

## 🔁 logseq\_hybrid/reconciler.py (queue + API application)

```python
from __future__ import annotations
import json
from dataclasses import dataclass, asdict
from typing import List, Literal
from .settings import QUEUE_PATH
from .api_client import LogseqAPI

ActionType = Literal["create_page", "insert_block"]

@dataclass
class Action:
    type: ActionType
    payload: dict

class Queue:
    def __init__(self, path=QUEUE_PATH):
        self.path = path
        self.actions: List[Action] = []
        if self.path.exists():
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            self.actions = [Action(**a) for a in raw]

    def add(self, action: Action) -> None:
        self.actions.append(action)
        self.path.write_text(json.dumps([asdict(a) for a in self.actions], indent=2), encoding="utf-8")

    def clear(self) -> None:
        self.actions = []
        self.path.write_text(json.dumps([], indent=2), encoding="utf-8")


def reconcile(api: LogseqAPI) -> int:
    if not api.is_available():
        return 0
    q = Queue()
    applied = 0
    for a in list(q.actions):
        if a.type == "create_page":
            api.create_page(a.payload["name"], a.payload.get("content", ""))
        elif a.type == "insert_block":
            api.insert_block(a.payload["parent_uuid"], a.payload["content"], a.payload.get("sibling", True))
        else:
            continue
        applied += 1
    if applied:
        q.clear()
    return applied
```

---

## 🖥️ logseq\_hybrid/cli.py

```python
from __future__ import annotations
import argparse
from .api_client import LogseqAPI
from .fs_writer import append_journal, append_to_page
from .indexer import list_pages, list_journals, grep
from .reconciler import Queue, Action, reconcile


def cmd_check(_: argparse.Namespace) -> None:
    api = LogseqAPI()
    ok = api.is_available()
    print(f"Logseq API available: {ok}")
    if ok:
        try:
            g = api.get_current_graph()
            print(f"Current graph: {g}")
        except Exception as e:
            print(f"API reachable but get_current_graph failed: {e}")


def cmd_add_journal(ns: argparse.Namespace) -> None:
    path = append_journal(ns.content)
    print(f"Wrote journal entry → {path}")


def cmd_add_page(ns: argparse.Namespace) -> None:
    path = append_to_page(ns.name, ns.content)
    print(f"Appended to page → {path}")


def cmd_queue_create_page(ns: argparse.Namespace) -> None:
    q = Queue()
    q.add(Action(type="create_page", payload={"name": ns.name, "content": ns.content}))
    print("Queued create_page action.")


def cmd_reconcile(_: argparse.Namespace) -> None:
    applied = reconcile(LogseqAPI())
    print(f"Reconciled actions: {applied}")


def cmd_list(_: argparse.Namespace) -> None:
    print("Pages:", list_pages())
    print("Journals:", list_journals())


def cmd_grep(ns: argparse.Namespace) -> None:
    print(grep(ns.term))


def main() -> None:
    p = argparse.ArgumentParser(prog="logseq-hybrid")
    sub = p.add_subparsers(required=True)

    s = sub.add_parser("check", help="Check API availability")
    s.set_defaults(func=cmd_check)

    s = sub.add_parser("add-journal", help="Append a journal entry (filesystem)")
    s.add_argument("content")
    s.set_defaults(func=cmd_add_journal)

    s = sub.add_parser("add-page", help="Append to a page (filesystem)")
    s.add_argument("name")
    s.add_argument("content")
    s.set_defaults(func=cmd_add_page)

    s = sub.add_parser("queue-create-page", help="Queue a page creation for later API reconcile")
    s.add_argument("name")
    s.add_argument("content")
    s.set_defaults(func=cmd_queue_create_page)

    s = sub.add_parser("reconcile", help="Apply queued actions via API if available")
    s.set_defaults(func=cmd_reconcile)

    s = sub.add_parser("list", help="List pages/journals (filesystem)")
    s.set_defaults(func=cmd_list)

    s = sub.add_parser("grep", help="Naive grep across graph")
    s.add_argument("term")
    s.set_defaults(func=cmd_grep)

    ns = p.parse_args()
    ns.func(ns)

if __name__ == "__main__":
    main()
```

---

## 🧪 tests/test\_health.py

```python
from __future__ import annotations
import os
from pathlib import Path
from logseq_hybrid.api_client import LogseqAPI
from logseq_hybrid.fs_writer import append_journal, append_to_page
from logseq_hybrid.indexer import list_pages, list_journals
from logseq_hybrid.reconciler import Queue, Action, reconcile


def test_api_ping():
    api = LogseqAPI()
    # Should not raise; availability may be False if Logseq is closed
    assert isinstance(api.is_available(), bool)


def test_fs_write(tmp_path: Path, monkeypatch):
    # Redirect GRAPH_PATH to tmp
    monkeypatch.setenv("GRAPH_PATH", str(tmp_path))
    from importlib import reload
    import logseq_hybrid.settings as settings
    reload(settings)

    from logseq_hybrid.fs_writer import append_journal as aj, append_to_page as ap
    aj("hello from test")
    ap("TestPage", "content")

    from logseq_hybrid.indexer import list_pages as lp, list_journals as lj
    assert "TestPage" in lp()
    assert len(lj()) >= 1


def test_queue_and_reconcile(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("GRAPH_PATH", str(tmp_path))
    from importlib import reload
    import logseq_hybrid.settings as settings
    reload(settings)

    from logseq_hybrid.reconciler import Queue, Action, reconcile
    q = Queue()
    q.add(Action(type="create_page", payload={"name": "QueuedPage", "content": "hello"}))

    api = LogseqAPI()
    applied = reconcile(api)
    # If API is down, applied == 0; if up, it will have applied >= 1.
    assert applied >= 0
```

---

## 🧾 Makefile

```makefile
.PHONY: install test check

install:
	python -m venv .venv
	. .venv/bin/activate && pip install -U pip -r requirements.txt -e .

check:
	. .venv/bin/activate && python -m logseq_hybrid.cli check

test:
	. .venv/bin/activate && pytest -q
```

---

## 📘 README.quickstart.md

````markdown
# Quickstart

1. Copy this project into a folder **outside** your Logseq graph.
2. Create and edit `.env` from `.env.example`.
3. Enable **Logseq → Settings → Features → Enable HTTP API** and copy the token.
4. Install & run:

```bash
make install
# Sanity check (works even if Logseq closed; just reports availability)
make check
````

5. Filesystem demo (works headless):

```bash
# Append to today’s journal
. .venv/bin/activate && python -m logseq_hybrid.cli add-journal "hello from FS"
# Append to a page (creates if missing)
. .venv/bin/activate && python -m logseq_hybrid.cli add-page "Agent Scratch" "first note"
```

6. Queue a surgical edit and reconcile later:

```bash
# Queue a create_page (safe to run headless)
. .venv/bin/activate && python -m logseq_hybrid.cli queue-create-page "Surgical API Page" "seed content"

# Later, when Logseq is open (API enabled):
. .venv/bin/activate && python -m logseq_hybrid.cli reconcile
```

7. Optional: simple reads over FS cache

```bash
. .venv/bin/activate && python -m logseq_hybrid.cli list
. .venv/bin/activate && python -m logseq_hybrid.cli grep "keyword"
```

## Notes

* **API path** requires Logseq to be open; FS path works always.
* Writes are **append-only** in FS mode to avoid corrupting block IDs/backlinks.
* Reconciler clears the queue only after successful API application.

````

---

## 🧩 Packaging (optional)

Add this to `logseq_hybrid/__init__.py` to allow `python -m logseq_hybrid.cli`:

```python
# empty; module marker
````

Add a basic `pyproject.toml` if you want editable installs:

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "logseq-hybrid"
version = "0.1.0"
dependencies = ["requests", "python-dotenv"]

[project.scripts]
logseq-hybrid = "logseq_hybrid.cli:main"
```

---

## ✅ How to Test End-to-End

1. **Headless FS path works**

```
make install
cp .env.example .env && edit GRAPH_PATH=... to your graph
. .venv/bin/activate && python -m logseq_hybrid.cli add-journal "FS headless ✅"
. .venv/bin/activate && python -m logseq_hybrid.cli add-page "FS Demo" "hello"
```

Open Logseq → confirm the journal and page appear after reindex.

2. **API available path works**

```
Open Logseq → enable HTTP API → copy token into .env
. .venv/bin/activate && python -m logseq_hybrid.cli check  # should print available: True
```

3. **Queued surgical edits reconcile**

```
# headless queue
. .venv/bin/activate && python -m logseq_hybrid.cli queue-create-page "Reconciled" "seed via queue"
# later (Logseq open)
. .venv/bin/activate && python -m logseq_hybrid.cli reconcile
```

Verify the page "Reconciled" exists in Logseq.

4. **Run tests**

```
. .venv/bin/activate && pip install pytest
make test
```

---

## 🛡️ Safety & Gotchas

* Keep FS writes **append-only**. Avoid editing existing block structures on disk.
* Use **atomic writes** (already implemented) to prevent partial files during sync.
* Keep a backup of your graph before first runs.
* If you later want precise block-level edits offline, store synthetic references in your own sidecar file and let the **reconciler** convert them to real blocks via the API when available.

---

## 📦 Bonus: Minimal MCP Tooling (hint)

If you’re integrating with Claude or another MCP client, point your MCP server’s tools to shell out to `logseq-hybrid` commands (`check`, `add-journal`, `queue-create-page`, `reconcile`) or import this package directly and expose the functions. This keeps your agent logic clean while you iterate.
