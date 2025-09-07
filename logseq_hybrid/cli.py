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
