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
