from pathlib import Path
import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field


class Settings(BaseModel):
    github_token: str | None = None
    llm_provider: str = "ollama"
    llm_api_key: str | None = None
    llm_model: str = "qwen2.5:7b"
    ollama_base_url: str = "http://127.0.0.1:11434"
    github_models_base_url: str = "https://models.inference.ai.azure.com"
    google_project: str | None = None
    google_location: str = "us-central1"
    research_depth: str = "standard"
    repository_limit: int = Field(default=10, ge=1, le=100)
    data_dir: Path = Field(default_factory=lambda: Path.home() / ".devscope")

    @classmethod
    def from_environment(cls) -> "Settings":
        load_dotenv()
        return cls(
            github_token=os.getenv("GITHUB_TOKEN") or None,
            llm_provider=os.getenv("LLM_PROVIDER", "ollama"),
            llm_api_key=os.getenv("LLM_API_KEY") or None,
            llm_model=os.getenv("LLM_MODEL", "qwen2.5:7b"),
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
            github_models_base_url=os.getenv("GITHUB_MODELS_BASE_URL", "https://models.inference.ai.azure.com"),
            google_project=os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCLOUD_PROJECT") or None,
            google_location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
            research_depth=os.getenv("RESEARCH_DEPTH", "standard"),
            repository_limit=int(os.getenv("REPOSITORY_LIMIT", "10")),
        )
