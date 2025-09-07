# CLI Design: `list-pages` Command

This document outlines the design for a new `list-pages` command in the `logseq-hybrid` CLI.

## 1. High-Level Goal

The command should provide a flexible way for users to list pages in their Logseq graph from the command line. It should be more powerful than the existing `list` command, offering sorting, filtering, and different output formats for scripting.

## 2. CLI Command Definition

The proposed new command is `list-pages`, with the following structure:

```bash
logseq-hybrid list-pages [OPTIONS]
```

**Options:**

*   `--sort-by {name,mtime}`: The field to sort the pages by.
    *   `name`: Sorts alphabetically by page name (default).
    *   `mtime`: Sorts by the last modification time.
*   `--reverse`: Reverses the sort order (e.g., descending for `name`, or newest-first for `mtime`).
*   `--format {text,json}`: The output format.
    *   `text`: A simple, newline-separated list of page names (default).
    *   `json`: A JSON array of objects, each containing detailed information about a page.
*   `--limit <N>`: An integer to limit the output to the top N results.

## 3. Output Formats

### Text (default)

This format is simple and ideal for human reading or for piping into other standard shell commands (`grep`, `fzf`, etc.).

```
Page One
Page Two
Another Page
```

### JSON

This format is for programmatic use, allowing scripts to easily parse the output. Each object in the array would contain:

```json
[
  {
    "name": "Page One",
    "file_path": "/path/to/your/graph/pages/Page One.md",
    "mtime": "2025-09-07T10:30:00Z",
    "size": 1234
  },
  {
    "name": "Page Two",
    "file_path": "/path/to/your/graph/pages/Page Two.md",
    "mtime": "2025-09-06T15:00:00Z",
    "size": 567
  }
]
```

## 4. Implementation Plan

1.  **`indexer.py`:**
    *   Create a new function, `get_pages_details()`, that replaces the simple `list_pages()`.
    *   This function will iterate through the files in `PAGES_DIR`.
    *   For each file, it will gather not just the `stem` (the name), but also the full path, modification time (`p.stat().st_mtime`), and size (`p.stat().st_size`).
    *   It will return a list of dictionaries or data objects, where each object represents a page with its full details.

2.  **`cli.py`:**
    *   Add a new subcommand parser for `list-pages`.
    *   Define the arguments: `--sort-by`, `--reverse`, `--format`, and `--limit`.
    *   Create a new handler function, `cmd_list_pages(ns)`.
    *   Inside this function:
        *   Call the new `indexer.get_pages_details()` to get the raw page data.
        *   Perform sorting on the list of pages based on the `--sort-by` and `--reverse` flags.
        *   If `--limit` is provided, truncate the list.
        *   Based on the `--format` flag, either print the page names in a simple loop (for `text` format) or use the `json` module to dump the list of page objects to standard output (for `json` format).
    *   Consider deprecating or removing the page-listing part of the old `list` command to avoid confusion.

## 5. Example Usage

*   **Get the 5 most recently modified pages:**
    ```bash
    logseq-hybrid list-pages --sort-by mtime --reverse --limit 5
    ```
*   **Get all pages as JSON for a script:**
    ```bash
    logseq-hybrid list-pages --format json > pages.json
    ```
*   **Find a page using `fzf` (a fuzzy finder):**
    ```bash
    logseq-hybrid list-pages | fzf
    ```
