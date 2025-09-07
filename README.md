# Logseq Hybrid

`logseq-hybrid` is a command-line tool that provides a "hybrid" workflow for interacting with your [Logseq](https://logseq.com/) graph. It allows you to capture information and modify your graph from the command line, both through direct filesystem manipulation and by interacting with the Logseq API.

This tool is designed for users who want to:

*   Quickly add notes to their journal or specific pages without opening the Logseq application.
*   Automate parts of their Logseq workflow using scripts.
*   Integrate Logseq with other command-line tools.

The "hybrid" approach means you can add content to your graph even when Logseq isn't running. The tool will write directly to the filesystem, and you can later reconcile these changes using the Logseq API when the application is open.

## Quickstart

For installation and initial setup instructions, please see the [Quickstart Guide](README.quickstart.md).

## Features

*   **Check API Status**: Verify that the Logseq API is available and get information about the current graph.
*   **Add to Journal (Offline)**: Append a new entry to today's journal page on the filesystem.
*   **Add to Page (Offline)**: Append content to a specific page on the filesystem.
*   **Queue Page Creation**: Add a "create page" action to a queue, which can be processed later when the API is available.
*   **Reconcile Queue**: Apply all queued actions (like creating pages) through the Logseq API.
*   **List Pages and Journals**: List all pages and journals in your graph from the filesystem.
*   **Grep**: Perform a simple text search across all pages and journals in your graph.

## Usage

```bash
logseq-hybrid [COMMAND] [OPTIONS]
```

### Commands

*   `check`: Check the availability of the Logseq API.
*   `add-journal <content>`: Append a new entry to today's journal.
*   `add-page <name> <content>`: Append content to a specific page.
*   `queue-create-page <name> <content>`: Queue a new page to be created via the API.
*   `reconcile`: Apply queued actions using the Logseq API.
*   `list`: List all pages and journals.
*   `grep <term>`: Search for a term across your entire graph.

### Examples

**Add a new note to your journal:**

```bash
logseq-hybrid add-journal "This is a new thought I had."
```

**Append a note to a page named "My Project":**

```bash
logseq-hybrid add-page "My Project" "I made some progress on the new feature today."
```

**Queue a new page to be created later:**

```bash
logseq-hybrid queue-create-page "New Book" "This is a book I want to read."
```

**Apply the queued actions:**

```bash
logseq-hybrid reconcile
```

## How it Works

`logseq-hybrid` interacts with your Logseq graph in two ways:

1.  **Filesystem**: For "offline" operations, the tool reads and writes directly to the Markdown files in your Logseq graph's `journals/` and `pages/` directories.
2.  **Logseq API**: For operations that require the Logseq application to be running, the tool communicates with the Logseq API. This is used for things like creating new pages in a way that Logseq will recognize immediately.

The `reconcile` command is the bridge between these two modes. It takes actions that have been queued up (like creating a new page) and applies them through the API, ensuring that your graph is consistent.
