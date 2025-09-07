from __future__ import annotations
import typer
from .api_client import LogseqAPI
from .fs_writer import append_journal, append_to_page
from .indexer import list_pages, list_journals, grep
from .reconciler import Queue, Action, reconcile

app = typer.Typer()


@app.command()
def check() -> None:
    """Check API availability"""
    api = LogseqAPI()
    ok = api.is_available()
    print(f"Logseq API available: {ok}")
    if ok:
        try:
            g = api.get_current_graph()
            print(f"Current graph: {g}")
        except Exception as e:
            print(f"API reachable but get_current_graph failed: {e}")


@app.command()
def add_journal(content: str) -> None:
    """Append a journal entry (filesystem)"""
    path = append_journal(content)
    print(f"Wrote journal entry → {path}")


@app.command()
def add_page(name: str, content: str) -> None:
    """Append to a page (filesystem)"""
    path = append_to_page(name, content)
    print(f"Appended to page → {path}")


@app.command()
def queue_create_page(name: str, content: str) -> None:
    """Queue a page creation for later API reconcile"""
    q = Queue()
    q.add(Action(type="create_page", payload={"name": name, "content": content}))
    print("Queued create_page action.")


@app.command()
def reconcile() -> None:
    """Apply queued actions via API if available"""
    applied = reconcile(LogseqAPI())
    print(f"Reconciled actions: {applied}")


@app.command()
def list() -> None:
    """List pages/journals (filesystem)"""
    print("Pages:", list_pages())
    print("Journals:", list_journals())


@app.command()
def grep(term: str) -> None:
    """Naive grep across graph"""
    print(grep(term))


def main() -> None:
    app()

if __name__ == "__main__":
    main()