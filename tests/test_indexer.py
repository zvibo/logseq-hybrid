from __future__ import annotations
from pathlib import Path
import pytest
from logseq_hybrid import indexer

def test_get_pages_details_empty(tmp_path: Path, monkeypatch):
    """Test that get_pages_details returns an empty list for an empty pages directory."""
    pages_dir = tmp_path / "pages"
    pages_dir.mkdir()
    monkeypatch.setattr(indexer, "PAGES_DIR", pages_dir)
    
    assert indexer.get_pages_details() == []

def test_get_pages_details_finds_pages(mock_graph: Path, monkeypatch):
    """Test that get_pages_details finds all pages and ignores journals."""
    monkeypatch.setattr(indexer, "PAGES_DIR", mock_graph / "pages")
    
    pages = indexer.get_pages_details()
    
    assert len(pages) == 3
    assert sorted([p["name"] for p in pages]) == ["Apple", "Banana", "Zebra"]

def test_get_pages_details_returns_correct_data(mock_graph: Path, monkeypatch):
    """Test that the data returned for a page is accurate."""
    monkeypatch.setattr(indexer, "PAGES_DIR", mock_graph / "pages")
    
    pages = indexer.get_pages_details()
    apple_page = next((p for p in pages if p["name"] == "Apple"), None)
    
    assert apple_page is not None
    assert apple_page["name"] == "Apple"
    assert Path(apple_page["file_path"]).name == "Apple.md"
    assert "mtime" in apple_page
    assert apple_page["size"] == len("This is a page about apples.")
