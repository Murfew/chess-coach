# chess-coach

A chess coach for your Chess.com games. It finds your biggest mistakes with
Stockfish and has Claude explain them from facts the engine checked, so the
explanations don't invent chess.

> Work in progress. Games come from the SQLite database built by
> [chesscom-fetch](https://github.com/Murfew/chesscom-fetch).

## Requirements

- Python 3.14+
- [uv](https://docs.astral.sh/uv/)

## Installation

```bash
git clone https://github.com/Murfew/chess-coach.git
cd chess-coach
uv sync
cp .env.example .env   # then add your ANTHROPIC_API_KEY
```

## Usage

Set `ANTHROPIC_API_KEY` in `.env` or your environment. To use another model,
set `CLAUDE_MODEL` (default: `claude-haiku-5-5`).

Ask Claude a question:

```bash
uv run chess-coach ask "Why is the Italian Game considered solid for beginners?"
```

The answer goes to stdout exactly as Claude wrote it, so `> answer.md` saves it.
If the answer is cut off, Claude declines, or the call fails, `chess-coach`
prints one line to stderr and exits with status 1.

Run `uv run chess-coach --help` to list commands.

## Development

```bash
uv run pytest                 # tests
uv run ruff check             # lint
uv run ruff format --check    # formatting
uv run mypy src tests         # types
uv run pre-commit install     # once: gitleaks runs before each commit
```

Every change goes through an issue, a branch and a squash-merged pull request.

## License

[MIT](LICENSE)
