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
