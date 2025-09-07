from __future__ import annotations
import pytest
import time
from pathlib import Path

@pytest.fixture
def mock_graph(tmp_path: Path) -> Path:
    """Creates a temporary mock Logseq graph."""
    graph_dir = tmp_path / "graph"
    pages_dir = graph_dir / "pages"
    journals_dir = graph_dir / "journals"
    pages_dir.mkdir(parents=True)
    journals_dir.mkdir(parents=True)

    # Create mock pages with controlled modification times
    (pages_dir / "Apple.md").write_text("This is a page about apples.")
    time.sleep(0.01)  # Ensure mtime is different
    (pages_dir / "Zebra.md").write_text("This is a page about zebras.")
    time.sleep(0.01)
    (pages_dir / "Banana.md").write_text("This is a page about bananas.")

    # Create a mock journal to be ignored
    (journals_dir / "2025_09_08.md").write_text("A journal entry.")

    return graph_dir
