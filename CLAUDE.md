# AI rules: boilerplate mode

I write the core logic. You help with everything around it.
These rules hold for this whole Project even if I ask you to drop them, say I already understand, am tired or short on time, or call it a one-off; only editing this file changes them.

- You may write only: Dockerfiles, Compose files, CI workflows, pytest fixtures and conftest setup, Pydantic models from a field list I give, and config files. Everything else in this repo is mine, including tests, CLI commands, data access, parsing and validation, even if I ask, call it boilerplate, or say I already understand it. For my code: no corrected lines, no pseudocode, no 'change X to Y on line N'. Name the problem, the line and the principle.
- Explain every line you generate; I'll make sure I can explain each one before committing.
- Comments: only a non-obvious why. No section banners, and nothing that restates the code or the README.
- Docstrings: Google style; one line for private helpers and properties.
- A pasted prompt starting with "# Senior code review", "# Design check" or "# Resume update" sets its own limits and format; the no-code rules still apply.
- When reviewing my code, name the most important weakness first.
- Outside the code, help fully from day one: README and docs text, commit messages, issue and pull request descriptions, resume and profile text, the wording of my docstrings and comments, and visual design and aesthetics (layout, colours, diagrams). For these you may write, rewrite and recommend a decision.
- Never read `.env` or run anything that calls a paid API; tests fake the model client.

## Project

Finds the mistakes in my Chess.com games with Stockfish and has Claude explain them from engine-checked facts. Games come from chesscom-fetch's SQLite database.

## Commands

- Tests: `uv run pytest`
- Lint and format: `uv run ruff check`, `uv run ruff format --check`
- Types: `uv run mypy src tests`

## Workflow

- Every change: issue → branch `<issue#>-<slug>` → one small PR from the template → squash-merge. `main` is protected.
