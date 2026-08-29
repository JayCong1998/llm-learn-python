"""Minimal LangChain model call with environment-based configuration."""

from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


class ConfigurationError(ValueError):
    """Raised when the project cannot find required configuration."""


@dataclass(frozen=True)
class Settings:
    api_key: str
    model: str


def get_settings() -> Settings:
    """Load this project's .env file and return model settings."""
    load_dotenv(Path(__file__).with_name(".env"))
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ConfigurationError(
            "OPENAI_API_KEY is missing. Copy .env.example to .env and add your key."
        )
    return Settings(api_key=api_key, model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"))


def ask_question(question: str) -> str:
    """Send one question to the configured chat model."""
    settings = get_settings()
    model = ChatOpenAI(model=settings.model, api_key=settings.api_key)
    return str(model.invoke(question).content)
