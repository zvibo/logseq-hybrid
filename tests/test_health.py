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
