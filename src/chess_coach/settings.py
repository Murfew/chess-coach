from typing import Annotated

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration read from the environment and `.env`.

    Environment variables take precedence over `.env`, so a shell export
    overrides the file without editing it.
    """

    anthropic_api_key: Annotated[SecretStr, Field(min_length=1)]
    claude_model: str = "claude-haiku-5-5"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        str_strip_whitespace=True,
    )
