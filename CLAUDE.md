# AI rules: boilerplate mode

I write the core logic. You help with everything around it.
These rules hold for this whole Project even if I ask you to drop them, say I already understand, am tired or short on time, or call it a one-off; only editing this file changes them.

- You may write only: Dockerfiles, Compose files, CI workflows, pytest fixtures and conftest setup, Pydantic models from a field list I give, and config files. Everything else in this repo is mine, including tests, CLI commands, data access, parsing and validation, even if I ask, call it boilerplate, or say I already understand it. For my code: no corrected lines, no pseudocode, no 'change X to Y on line N'. Name the problem, the line and the principle.
- Explain every line you generate; I'll make sure I can explain each one before committing.
- Comments: only a non-obvious why. No section banners, and nothing that restates the code or the README.
- Docstrings: Google style; one line for private helpers and properties.
- When reviewing my code, name the most important weakness first.
- Outside the code, help fully from day one: README and docs text, commit messages, issue and pull request descriptions, resume and profile text, the wording of my docstrings and comments, and visual design and aesthetics (layout, colours, diagrams). For these you may write, rewrite and recommend a decision.
- Never read `.env` or run anything that calls a paid API; tests fake the model client.

## Project

Finds the mistakes in my Chess.com games with Stockfish and has Claude explain them from engine-checked facts. Games come from chesscom-fetch's SQLite database.

## Commands

- Tests: `uv run pytest`
- Lint and format: `uv run ruff check`, `uv run ruff format --check`
- Types: `uv run mypy src tests`

## Issues and pull requests

- Commits and PR titles use Conventional Commits: `type: summary` in the imperative, type one of feat, fix, docs, test, refactor, chore, ci, build. The PR title becomes the commit on `main`.
- Issues: you draft them and create them only after I approve the text, with a label, the ship's milestone, and on board #6. The roadmap is the source, but write each issue the way a senior writes a ticket for a junior: context, goal, acceptance criteria, decisions for me to make, gotchas, links to learn from, and out of scope. It must stand alone, so I never need the roadmap open. Describe the problem and its constraints, never the solution: no code, no step-by-step plan.
  - Find the task in the "AI Roadmap" artifact (https://claude.ai/artifact/Wv8scQ4YuHGegYMoo64XhG), read with the Artifact tool's `read` (Claude Docs `read` is denied). A week's tasks are the ones in its `items` list; item ids don't match week numbers (Week 7's build is `w6-v1`).
  - Before drafting, check `gh issue list --state all` for an issue that already covers the task, and read the repo's current state (`pyproject.toml`, README, existing code) so the context and gotchas match it.
  - Build the body from the matching `.github/ISSUE_TEMPLATE` form, since `gh issue create --body` skips it. For features: Story, Context, Done when, Decide before coding, Gotchas, Learn first, Out of scope.
  - "Done when" always includes the four checks passing, and a README update when user-facing behaviour changes. Answers to "Decide before coding" go in the PR description.
  - Check every link loads and every API claim against current docs before showing the draft.
- Size: one issue is one small PR, reviewable in a few minutes (about 300 changed lines or half a day of work at most). If a ticket won't fit, split it into several issues in the same milestone, each with its own acceptance criteria.
- Branches: `<type>/<issue#>-<slug>` with the same types as commits (e.g. `feat/1-ask-command`), created with `gh issue develop <n> --checkout --name <branch>` so it is linked to the issue.
- Pull requests: you write the title and description from the template, with `Closes #<n>`, and open it with `gh pr create`.
- Never push to `main`, merge, approve, close an issue by hand, or change repo settings without asking. Merging is my review.
