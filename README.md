# Allium

Offline-first digital companion and AI orchestrator for ZENO.

## Task 1.1 status

This repository is being built incrementally from **ALLIUM-SPEC-v2.0.4-CONSOLIDATED**. Only Task 1.1 (project setup) is in scope until its checkpoint is verified.

### MVP principles
- Offline-first reasoning with local AI.
- Permission Manager is the sole security authority.
- LLM output is data for Planner validation; it never executes OS actions directly.
- Secrets belong in `.env`; non-sensitive configuration belongs in `data/config.json`.
- User data is local by default and is not uploaded automatically.

## Windows setup

Python 3.10+ is required. Create the virtual environment with:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Copy `data/.env.example` to `data/.env` and fill only the required local secrets. Never commit `.env`.

Run the entry point with:

```powershell
python src/main.py
```

Expected startup output:

```text
Allium starting...
```

## Repository structure

The repository follows Section 21 of the master specification. Future-phase modules are represented structurally only; no future-phase functionality is implemented in Task 1.1.

## Specification

- Document ID: `ALLIUM-SPEC-v2.0.4-CONSOLIDATED`
- Date: 2026-08-19
- Content SHA: `a3f8c92d1e4b7a6f5c0d9e2b1a3c4d5e6f7a8b9c0`

## License

MIT. See `LICENSE`.
