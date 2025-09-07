from __future__ import annotations
import pytest

# TODO: Implement tests

from pathlib import Path
import subprocess
import json


import sys

def run_cli_command(command: list[str], mock_graph: Path) -> str:
    """Helper function to run a CLI command in a subprocess."""
    env = {"GRAPH_PATH": str(mock_graph)}
    # Use sys.executable to ensure we're running the CLI with the same python interpreter
    # that's running pytest. This avoids PATH issues with virtual environments.
    cmd = [sys.executable, "-m", "logseq_hybrid.cli"] + command
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=env,
        check=True,
    )
    return result.stdout

def test_list_pages_default_sort(mock_graph: Path):
    """Test default sorting (by name, ascending)."""
    output = run_cli_command(["list-pages"], mock_graph)
    assert output.strip().split("\n") == ["Apple", "Banana", "Zebra"]

def test_list_pages_sort_name_reverse(mock_graph: Path):
    """Test sorting by name, descending."""
    output = run_cli_command(["list-pages", "--sort-by", "name", "--reverse"], mock_graph)
    assert output.strip().split("\n") == ["Zebra", "Banana", "Apple"]

def test_list_pages_sort_mtime(mock_graph: Path):
    """Test sorting by modification time, ascending (oldest first)."""
    output = run_cli_command(["list-pages", "--sort-by", "mtime"], mock_graph)
    assert output.strip().split("\n") == ["Apple", "Zebra", "Banana"]

def test_list_pages_sort_mtime_reverse(mock_graph: Path):
    """Test sorting by modification time, descending (newest first)."""
    output = run_cli_command(["list-pages", "--sort-by", "mtime", "--reverse"], mock_graph)
    assert output.strip().split("\n") == ["Banana", "Zebra", "Apple"]

def test_list_pages_limit(mock_graph: Path):
    """Test the --limit option."""
    output = run_cli_command(["list-pages", "--limit", "2"], mock_graph)
    assert output.strip().split("\n") == ["Apple", "Banana"]

def test_list_pages_format_json(mock_graph: Path):
    """Test the --format json option."""
    output = run_cli_command(["list-pages", "--format", "json"], mock_graph)
    data = json.loads(output)
    assert len(data) == 3
    assert "name" in data[0]
    assert "file_path" in data[0]
    assert "mtime" in data[0]
    assert "size" in data[0]

def test_list_pages_combined_options(mock_graph: Path):
    """Test a combination of options."""
    output = run_cli_command(
        ["list-pages", "--sort-by", "mtime", "--reverse", "--limit", "2", "--format", "json"],
        mock_graph,
    )
    data = json.loads(output)
    assert len(data) == 2
    assert data[0]["name"] == "Banana"
    assert data[1]["name"] == "Zebra"
