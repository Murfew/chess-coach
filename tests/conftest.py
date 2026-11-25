from pathlib import Path

import pytest
from anthropic import Anthropic


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
    return Anthropic(api_key="test-key", max_retries=0)
