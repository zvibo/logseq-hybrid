# Quickstart Guide

This guide will walk you through the initial setup of `logseq-hybrid`.

## Installation

1.  **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd logseq-hybrid
    ```

2.  **Create a virtual environment:**

    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install the package in development mode:**

    This command installs the package and its dependencies. The `-e` flag (for "editable") means that any changes you make to the source code will be immediately available when you run the command-line tool.

    ```bash
    pip install -e .
    ```

## Shell Completion

To enable shell autocompletion for the `logseq-hybrid` command, run the following command and follow the on-screen instructions. This will make it easier to use the tool by allowing you to tab-complete commands and arguments.

```bash
logseq-hybrid --install-completion bash
```

After installation, you may need to restart your shell or source your shell's configuration file (e.g., `source ~/.bashrc`) for the changes to take effect.