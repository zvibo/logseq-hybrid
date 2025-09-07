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
            # A POST to /api with an empty method is the best way to check for liveness
            r = self.session.post(f"{self.base_url}/api", timeout=1.5, json={"method": "", "args": []})
            return r.status_code == 400  # This is expected for a bogus method
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
