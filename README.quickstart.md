# Quickstart

1. Copy this project into a folder **outside** your Logseq graph.
2. Create and edit `.env` from `.env.example`.
3. Enable **Logseq → Settings → Features → Enable HTTP API** and copy the token.
4. Install & run:

```bash
make install
# Sanity check (works even if Logseq closed; just reports availability)
make check
```

5. Filesystem demo (works headless):

```bash
# Append to today’s journal
. .venv/bin/activate && python -m logseq_hybrid.cli add-journal "hello from FS"
# Append to a page (creates if missing)
. .venv/bin/activate && python -m logseq_hybrid.cli add-page "Agent Scratch" "first note"
```

6. Queue a surgical edit and reconcile later:

```bash
# Queue a create_page (safe to run headless)
. .venv/bin/activate && python -m logseq_hybrid.cli queue-create-page "Surgical API Page" "seed content"

# Later, when Logseq is open (API enabled):
. .venv/bin/activate && python -m logseq_hybrid.cli reconcile
```

7. Optional: simple reads over FS cache

```bash
. .venv/bin/activate && python -m logseq_hybrid.cli list
. .venv/bin/activate && python -m logseq_hybrid.cli grep "keyword"
```

## Notes

* **API path** requires Logseq to be open; FS path works always.
* Writes are **append-only** in FS mode to avoid corrupting block IDs/backlinks.
* Reconciler clears the queue only after successful API application.
