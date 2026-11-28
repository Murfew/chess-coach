from typing import Annotated

import typer
from pydantic import ValidationError
from rich.console import Console
from rich.markup import escape

from chess_coach.claude import ClaudeError, build_client, get_answer
from chess_coach.settings import Settings

app = typer.Typer()
console = Console()
err_console = Console(stderr=True)


def _print_error(message: str) -> None:
    """Print a message to stderr after a red "Error:" label."""
    err_console.print(f"[bold red]Error:[/bold red] {escape(message)}")


def _load_settings() -> Settings:
    """Load settings, or print each problem and exit if any are invalid."""
    try:
        settings = Settings()
    except ValidationError as err:
        for problem in err.errors():
            env_var = str(problem["loc"][0]).upper()

            if problem["type"] == "missing" or (
                env_var == "ANTHROPIC_API_KEY" and problem["type"] == "too_short"
            ):
                _print_error(
                    f"{env_var} is not set; add it to your environment or .env."
                )
            else:
                _print_error(
                    f"{env_var} is invalid ({problem['msg'].lower()}); check your environment or .env."
                )
        raise typer.Exit(1) from err
    else:
        return settings


@app.callback()
def main() -> None:
    """Find and explain the mistakes in your Chess.com games."""


@app.command()
def ask(
    question: Annotated[
        str, typer.Argument(help="The question to ask Claude, in quotes.")
    ],
) -> None:
    """Ask Claude a question and print its answer."""
    question = question.strip()
    if not question:
        _print_error(
            'the question is empty; pass it in quotes, e.g. chess-coach ask "…".'
        )
        raise typer.Exit(1)

    settings = _load_settings()
    client = build_client(settings.anthropic_api_key.get_secret_value())
    model = settings.claude_model

    try:
        answer, outcome = get_answer(client, model, question)
    except ClaudeError as err:
        _print_error(str(err))
        raise typer.Exit(1) from err

    match outcome:
        case "answered":
            console.print(
                answer, soft_wrap=True, highlight=False, markup=False, emoji=False
            )
        case "cut off":
            err_console.print(
                "[yellow]Stopped:[/yellow] Claude's answer was cut off before it finished; try a narrower question."
            )
            raise typer.Exit(1)
        case "declined":
            err_console.print(
                "[yellow]Stopped:[/yellow] Claude declined to answer this question."
            )
            raise typer.Exit(1)
