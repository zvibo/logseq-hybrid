# Test Plan: `list-pages` Command

This document outlines the testing strategy for the `list-pages` command to ensure its functionality, options, and output formats work as expected.

## 1. Testing Strategy

We will use a combination of **unit tests** and **functional tests**.

*   **Unit Tests:** These will target the new logic in `indexer.py` (`get_pages_details`). They will run in isolation to verify that the function correctly gathers page information from the filesystem without involving the CLI argument parser.
*   **Functional Tests:** These will test the command-line interface itself. We will execute the `logseq-hybrid list-pages` command as a subprocess, simulating how a user would run it. These tests will check the command's standard output against expected results for various combinations of arguments.

All tests will be written using the `pytest` framework.

## 2. Test Environment Setup

A `pytest` fixture will be created to set up a temporary, mock Logseq graph on the filesystem for each test run. This ensures that the tests are isolated and repeatable.

The fixture (`mock_graph`) will:
1.  Create a temporary root directory.
2.  Create the necessary subdirectories: `pages/` and `journals/`.
3.  Create a set of mock page files with known names, content, and, most importantly, **controlled modification times**.
    *   `pages/Apple.md` (created first, oldest `mtime`)
    *   `pages/Zebra.md` (created second)
    *   `pages/Banana.md` (created third, newest `mtime`)
4.  Create a mock journal file to ensure it is **not** included in the results.
    *   `journals/2025_09_08.md`
5.  Pass the path to this temporary graph to the tests, which will point the `GRAPH_PATH` environment variable to it.

## 3. Unit Tests (for `indexer.py`)

These tests will be located in a new file, `tests/test_indexer.py`.

*   **`test_get_pages_details_empty`**:
    *   **Setup:** An empty `pages` directory.
    *   **Action:** Call `indexer.get_pages_details()`.
    *   **Assert:** The function returns an empty list.
*   **`test_get_pages_details_finds_pages`**:
    *   **Setup:** The `mock_graph` fixture.
    *   **Action:** Call `indexer.get_pages_details()`.
    *   **Assert:** The function returns a list with exactly 3 items.
    *   **Assert:** The names of the pages found are "Apple", "Zebra", and "Banana".
*   **`test_get_pages_details_returns_correct_data`**:
    *   **Setup:** The `mock_graph` fixture.
    *   **Action:** Call `indexer.get_pages_details()` and inspect the entry for "Apple.md".
    *   **Assert:** The dictionary/object for "Apple" contains the correct `name`, `file_path`, `mtime`, and `size`.

## 4. Functional Tests (for `cli.py`)

These tests will be located in a new file, `tests/test_cli.py` (or a more specific `test_cli_list_pages.py`).

*   **`test_list_pages_default_sort`**:
    *   **Action:** Run `logseq-hybrid list-pages`.
    *   **Assert:** The output is the string "Apple\nBanana\nZebra\n".
*   **`test_list_pages_sort_name_reverse`**:
    *   **Action:** Run `logseq-hybrid list-pages --sort-by name --reverse`.
    *   **Assert:** The output is the string "Zebra\nBanana\nApple\n".
*   **`test_list_pages_sort_mtime`**:
    *   **Action:** Run `logseq-hybrid list-pages --sort-by mtime`.
    *   **Assert:** The output is "Apple\nZebra\nBanana\n" (oldest to newest).
*   **`test_list_pages_sort_mtime_reverse`**:
    *   **Action:** Run `logseq-hybrid list-pages --sort-by mtime --reverse`.
    *   **Assert:** The output is "Banana\nZebra\nApple\n" (newest to oldest).
*   **`test_list_pages_limit`**:
    *   **Action:** Run `logseq-hybrid list-pages --limit 2`.
    *   **Assert:** The output is "Apple\nBanana\n".
*   **`test_list_pages_format_json`**:
    *   **Action:** Run `logseq-hybrid list-pages --format json`.
    *   **Assert:** The output is a valid JSON string.
    *   **Assert:** After parsing, the result is a list of 3 objects, each containing the keys `name`, `file_path`, `mtime`, and `size`.
*   **`test_list_pages_combined_options`**:
    *   **Action:** Run `logseq-hybrid list-pages --sort-by mtime --reverse --limit 2 --format json`.
    *   **Assert:** The output is a valid JSON string.
    *   **Assert:** After parsing, the result is a list of 2 objects.
    *   **Assert:** The first object in the list is the "Banana" page, and the second is the "Zebra" page.
