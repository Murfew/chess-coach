import pytest
from anthropic import Anthropic, AuthenticationError
from anthropic.types import Message, StopReason
from fake_claude import (
    FAKE_API_KEY,
    ReplyWith,
    make_message,
    make_status_error,
    text_block,
)
from httpx2 import codes
from typer.testing import CliRunner

from chess_coach.cli import app


@pytest.mark.usefixtures("api_key", "cli_client")
def test_ask_prints_answer_verbatim(runner: CliRunner, reply_with: ReplyWith) -> None:
    answer = "[link] [/i] :smile: " + "a" * 100
    reply_with(make_message([text_block(answer)], "end_turn"))

    result = runner.invoke(app, ["ask", "why?"])

    assert result.exit_code == 0
    assert answer + "\n" == result.stdout
    assert not result.stderr


@pytest.mark.usefixtures("api_key", "cli_client")
def test_ask_without_question_shows_usage(runner: CliRunner) -> None:
    result = runner.invoke(app, ["ask"])

    assert result.exit_code == 2
    assert "Missing argument" in result.stderr


@pytest.mark.parametrize(
    "empty_value",
    [pytest.param("", id="empty"), pytest.param("    ", id="whitespace")],
)
@pytest.mark.usefixtures("api_key", "cli_client")
def test_ask_rejects_blank_question(
    empty_value: str, reply_with: ReplyWith, runner: CliRunner
) -> None:
    reply_with(AssertionError("API should not be called"))

    result = runner.invoke(app, ["ask", empty_value])

    assert isinstance(result.exception, SystemExit)
    assert result.exit_code == 1
    assert "question is empty" in result.stderr


@pytest.mark.usefixtures("cli_client")
def test_ask_without_api_key_names_it(runner: CliRunner, reply_with: ReplyWith) -> None:
    reply_with(AssertionError("API should not be called"))

    result = runner.invoke(app, ["ask", "why?"])

    assert isinstance(result.exception, SystemExit)
    assert result.exit_code == 1
    assert "ANTHROPIC_API_KEY is not set" in result.stderr
    assert len(result.stderr.splitlines()) == 1


@pytest.mark.parametrize(
    "api_key_value", [pytest.param("", id="empty"), pytest.param("  ", id="whitespace")]
)
@pytest.mark.usefixtures("cli_client")
def test_ask_with_empty_api_key_names_it(
    runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
    api_key_value: str,
    reply_with: ReplyWith,
) -> None:
    reply_with(AssertionError("API should not be called"))
    monkeypatch.setenv("ANTHROPIC_API_KEY", api_key_value)

    result = runner.invoke(app, ["ask", "why?"])

    assert isinstance(result.exception, SystemExit)
    assert result.exit_code == 1
    assert "ANTHROPIC_API_KEY is not set" in result.stderr
    assert len(result.stderr.splitlines()) == 1


@pytest.mark.parametrize(
    ("stop_reason", "output", "content"),
    [
        pytest.param(
            "max_tokens",
            "cut off",
            "some content",
            id="cut-off",
        ),
        pytest.param("refusal", "declined", "", id="declined"),
    ],
)
@pytest.mark.usefixtures("api_key", "cli_client")
def test_ask_reports_unfinished_answer(
    stop_reason: StopReason,
    output: str,
    content: str,
    reply_with: ReplyWith,
    runner: CliRunner,
) -> None:
    reply_with(make_message([text_block(content)], stop_reason))

    result = runner.invoke(app, ["ask", "why?"])

    assert result.exit_code == 1
    assert not result.stdout
    assert output in result.stderr


@pytest.mark.usefixtures("api_key", "cli_client")
def test_ask_reports_claude_error(reply_with: ReplyWith, runner: CliRunner) -> None:
    reply_with(make_status_error(AuthenticationError, codes.UNAUTHORIZED))

    result = runner.invoke(app, ["ask", "why?"])

    assert result.exit_code == 1
    assert "Error: " in result.stderr
    assert "ANTHROPIC_API_KEY" in result.stderr
    assert "Traceback" not in result.stderr
    assert FAKE_API_KEY not in result.stderr
    assert FAKE_API_KEY not in result.stdout


@pytest.mark.usefixtures("api_key")
def test_ask_sends_stripped_question(
    monkeypatch: pytest.MonkeyPatch, runner: CliRunner, cli_client: Anthropic
) -> None:
    calls = []

    def fake_create(**kwargs: object) -> Message:
        calls.append(kwargs["messages"])
        return make_message([text_block("Some answer...")], "end_turn")

    monkeypatch.setattr(cli_client.messages, "create", fake_create)

    result = runner.invoke(app, ["ask", "  why?  "])

    assert result.exit_code == 0
    assert len(calls) == 1
    assert calls[0] == [{"role": "user", "content": "why?"}]


@pytest.mark.usefixtures("api_key")
def test_ask_sends_configured_model(
    monkeypatch: pytest.MonkeyPatch, runner: CliRunner, cli_client: Anthropic
) -> None:
    calls = []
    sonnet = "claude-sonnet-5-5"

    def fake_create(**kwargs: object) -> Message:
        calls.append(kwargs["model"])
        return make_message([text_block("Some answer...")], "end_turn")

    monkeypatch.setattr(cli_client.messages, "create", fake_create)
    monkeypatch.setenv("CLAUDE_MODEL", sonnet)

    result = runner.invoke(app, ["ask", "why?"])

    assert result.exit_code == 0
    assert len(calls) == 1
    assert calls[0] == sonnet


def test_help_lists_ask(runner: CliRunner) -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Ask Claude a question and print its answer." in result.stdout
    assert "Find and explain the mistakes in your Chess.com games." in result.stdout
