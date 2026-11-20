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

Coming with v1.

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
