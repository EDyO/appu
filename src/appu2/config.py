from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


__project_name__ = "appu"

ROOT_PROJECT_PATH = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    # Debug mode
    debug: bool = Field(default=False)

    # Meta Behavior
    model_config = SettingsConfigDict(
        env_file=ROOT_PROJECT_PATH / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        # Keep this here, in case we eventually use docker secrets
        # secrets_dir="/run/secrets",
    )


settings = Settings()
