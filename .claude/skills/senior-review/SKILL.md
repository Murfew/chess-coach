---
description: Review the current branch against main as a senior engineer, most important weakness first.
argument-hint: "[focus]"
disable-model-invocation: true
allowed-tools: Bash(gh issue view *) Bash(uv run *)
context: fork
agent: reviewer
---

Review this branch as a senior engineer would before approving it. Extra focus from the author, if any: $ARGUMENTS

## Linked issue

Branch: !`git branch --show-current`

The issue number is the digits after the type, as in `feat/1-ask-command` for issue 1. Read it with `gh issue view <n>` before reviewing; if the branch has no number, review without an issue.

## Uncommitted changes (not in the diff below)

!`git status --short`

## Commits

!`git log main..HEAD --oneline`

## Diff

!`git diff main...HEAD --stat`

!`git diff main...HEAD`

## What to check, in priority order

1. Meets the issue: everything in "Done when" is done, nothing outside its scope; "Decide before coding" has answers ready for the PR description.
2. Correctness: bugs, unhandled edge cases (missing games, bad input, Claude client errors), silently swallowed failures.
3. Design: one job per module, names that say what the code does, coupling that will make the next change harder.
4. Tests: behaviour and failure paths covered, not only the happy path; the model client is faked; each test would fail if the code broke.
5. Types and safety: honest hints, no `Any` escape hatches, no secrets or `.env` reads, no paid API calls.
6. Project rules from CLAUDE.md: Google-style docstrings, comments only for a non-obvious why, README updated if user-facing behaviour changed, Conventional Commits, diff under about 300 changed lines.

Run `uv run pytest`, `uv run ruff check`, `uv run ruff format --check` and `uv run mypy src tests`, and report their actual results. Don't repeat what those tools already flag.
