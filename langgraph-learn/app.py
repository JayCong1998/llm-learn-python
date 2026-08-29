"""Minimal LangGraph workflow with a single model node."""

from dataclasses import dataclass
import os
from pathlib import Path
from typing import TypedDict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph


class ConfigurationError(ValueError):
    """Raised when the project cannot find required configuration."""


@dataclass(frozen=True)
class Settings:
    api_key: str
    model: str


class GraphState(TypedDict):
    question: str
    answer: str


def get_settings() -> Settings:
    """Load this project's .env file and return model settings."""
    load_dotenv(Path(__file__).with_name(".env"))
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ConfigurationError(
            "OPENAI_API_KEY is missing. Copy .env.example to .env and add your key."
        )
    return Settings(api_key=api_key, model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"))


def build_graph():
    """Build START -> call_model -> END for the configured chat model."""
    settings = get_settings()
    model = ChatOpenAI(model=settings.model, api_key=settings.api_key)

    def call_model(state: GraphState) -> dict[str, str]:
        return {"answer": str(model.invoke(state["question"]).content)}

    workflow = StateGraph(GraphState)
    workflow.add_node("call_model", call_model)
    workflow.add_edge(START, "call_model")
    workflow.add_edge("call_model", END)
    return workflow.compile()
