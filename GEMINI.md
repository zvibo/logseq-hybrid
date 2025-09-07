# Gemini Workspace Configuration

This file configures the Gemini CLI for this workspace.

## Ignored Files

The following files and directories are ignored by Gemini:

- .venv/
- GEMINI.md
- .env
- .env~
- .pytest_cache/
- __pycache__/
- *.pyc
- *.egg-info/
- .agent_tmp/

## Development Installation

To install the `logseq-hybrid` package in "live" or "development" mode, use the following command. This allows you to run the package from the command line without creating artifacts outside of the virtual environment.

```bash
pip install -e .
```