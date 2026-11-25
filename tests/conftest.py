from pathlib import Path

import pytest
from anthropic import Anthropic
from anthropic.types import Message
from fake_claude import FAKE_API_KEY, ReplyWith


@pytest.fixture(autouse=True)
def isolated_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Keep the real environment and `.env` out of every test."""
    for name in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "CLAUDE_MODEL"):
        monkeypatch.delenv(name, raising=False)
    # Settings reads `.env` from the working directory, so run somewhere empty.
    monkeypatch.chdir(tmp_path)


@pytest.fixture
def client() -> Anthropic:
    """A real client with a dummy key; tests replace `client.messages.create`."""
    return Anthropic(api_key=FAKE_API_KEY, max_retries=0)


@pytest.fixture
def reply_with(client: Anthropic, monkeypatch: pytest.MonkeyPatch) -> ReplyWith:
    """Make `client.messages.create` return the given message or raise the error."""

    def set_reply(reply: Message | Exception) -> None:
        def fake_create(**kwargs: object) -> Message:
            if isinstance(reply, Exception):
                raise reply
            return reply

        monkeypatch.setattr(client.messages, "create", fake_create)

    return set_reply
