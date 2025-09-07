from __future__ import annotations
import argparse
import json
from .api_client import LogseqAPI
from .fs_writer import append_journal, append_to_page
from .indexer import get_pages_details, list_journals, grep
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


def cmd_list_journals(_: argparse.Namespace) -> None:
    print("Journals:", list_journals())


def cmd_grep(ns: argparse.Namespace) -> None:
    print(grep(ns.term))


def cmd_list_pages(ns: argparse.Namespace) -> None:
    pages = get_pages_details()
    
    # Sort
    sort_key = "name" if ns.sort_by == "name" else "mtime"
    pages.sort(key=lambda p: p[sort_key], reverse=ns.reverse)

    # Limit
    if ns.limit:
        pages = pages[:ns.limit]

    # Format
    if ns.format == "json":
        print(json.dumps(pages, indent=2))
    else:
        for p in pages:
            print(p["name"])


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

    s = sub.add_parser("list-journals", help="List journals (filesystem)")
    s.set_defaults(func=cmd_list_journals)

    s = sub.add_parser("grep", help="Naive grep across graph")
    s.add_argument("term")
    s.set_defaults(func=cmd_grep)

    # New list-pages command
    s = sub.add_parser("list-pages", help="List pages with sorting and formatting")
    s.add_argument("--sort-by", choices=["name", "mtime"], default="name", help="Field to sort by")
    s.add_argument("--reverse", action="store_true", help="Reverse the sort order")
    s.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    s.add_argument("--limit", type=int, help="Limit the number of results")
    s.set_defaults(func=cmd_list_pages)

    ns = p.parse_args()
    ns.func(ns)

if __name__ == "__main__":
    main()
