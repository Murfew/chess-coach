from pathlib import Path

import pytest
from pydantic import ValidationError

from chess_coach.settings import Settings

FAKE_API_KEY = "fake-api-key"


def test_missing_api_key_raises() -> None:
    with pytest.raises(ValidationError):
        Settings()


def test_api_key_hidden_in_repr_and_str(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", FAKE_API_KEY)

    settings = Settings()

    assert FAKE_API_KEY not in repr(settings)
    assert FAKE_API_KEY not in str(settings)


def test_model_defaults_to_haiku(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", FAKE_API_KEY)

    settings = Settings()

    assert settings.claude_model == "claude-haiku-5-5"


def test_ignores_unknown_dotenv_keys(tmp_path: Path) -> None:
    unknown_key = "UNKNOWN_KEY"
    env_file = tmp_path / ".env"
    env_file.write_text(
        f"ANTHROPIC_API_KEY={FAKE_API_KEY}\n{unknown_key}=should_be_ignored\n"
    )

    Settings(_env_file=env_file)
