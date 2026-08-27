from typing import Protocol
import httpx


class LLMProvider(Protocol):
    def complete(self, prompt: str) -> str: ...

    def embed(self, text: str) -> list[float]: ...


class UnconfiguredProvider:
    def complete(self, prompt: str) -> str:
        raise RuntimeError("No LLM provider configured. Set LLM_PROVIDER and LLM_API_KEY.")

    def embed(self, text: str) -> list[float]:
        raise RuntimeError("No LLM provider configured.")


class OllamaProvider:
    """Free local provider backed by an Ollama-served open-weight model."""

    def __init__(self, model: str = "llama3.2", base_url: str = "http://127.0.0.1:11434", timeout: float = 120.0):
        self.model = model
        self.client = httpx.Client(base_url=base_url.rstrip("/"), timeout=timeout)

    def complete(self, prompt: str) -> str:
        try:
            response = self.client.post(
                "/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                    "options": {"temperature": 0.1},
                },
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Ollama is unavailable at {self.client.base_url}. Run `ollama run {self.model}` first.") from exc
        return response.json().get("response", "")

    def embed(self, text: str) -> list[float]:
        return self.embed_many([text])[0]

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        try:
            response = self.client.post("/api/embed", json={"model": self.model, "input": texts})
            response.raise_for_status()
            return response.json().get("embeddings", [])
        except (httpx.HTTPError, KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"Ollama embeddings failed for model {self.model}.") from exc


class GitHubModelsProvider:
    """GitHub Models provider using the user's GitHub token."""

    def __init__(self, token: str, model: str = "gpt-4o-mini", base_url: str = "https://models.inference.ai.azure.com", timeout: float = 120.0):
        self.model = model
        self.client = httpx.Client(base_url=base_url.rstrip("/"), headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}, timeout=timeout)

    def complete(self, prompt: str) -> str:
        try:
            response = self.client.post("/chat/completions", json={"model": self.model, "messages": [{"role": "user", "content": prompt}]})
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise RuntimeError("GitHub Models request failed. Check GITHUB_TOKEN and model access.") from exc
        return response.json()["choices"][0]["message"]["content"]


class GeminiProvider:
    """Gemini through Vertex AI using local Google Application Default Credentials."""

    def __init__(self, project: str, model: str = "gemini-2.5-flash", location: str = "us-central1", timeout: float = 120.0):
        self.project = project
        self.model = model
        self.location = location
        self.client = httpx.Client(timeout=timeout)

    def complete(self, prompt: str) -> str:
        try:
            import google.auth
            from google.auth.transport.requests import Request
            credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
            credentials.refresh(Request())
            endpoint = f"https://{self.location}-aiplatform.googleapis.com/v1/projects/{self.project}/locations/{self.location}/publishers/google/models/{self.model}:generateContent"
            response = self.client.post(endpoint, headers={"Authorization": f"Bearer {credentials.token}"}, json={"contents": [{"role": "user", "parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"}})
            response.raise_for_status()
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except ImportError as exc:
            raise RuntimeError("Gemini support requires google-auth. Run `pip install -e .`.") from exc
        except Exception as exc:
            raise RuntimeError("Gemini authentication or Vertex AI request failed. Run `devscope auth google` and check your project.") from exc


def create_provider(settings) -> LLMProvider:
    if settings.llm_provider.lower() == "ollama":
        return OllamaProvider(settings.llm_model, settings.ollama_base_url)
    if settings.llm_provider.lower() in {"github-models", "github_models"}:
        if not settings.github_token:
            raise RuntimeError("github-models requires GITHUB_TOKEN. Run `devscope init` and configure it.")
        return GitHubModelsProvider(settings.github_token, settings.llm_model, settings.github_models_base_url)
    if settings.llm_provider.lower() in {"gemini", "google", "vertex"}:
        if not settings.google_project:
            raise RuntimeError("Gemini requires GOOGLE_CLOUD_PROJECT. Run `devscope auth google --project YOUR_PROJECT_ID`.")
        return GeminiProvider(settings.google_project, settings.llm_model, settings.google_location)
    return UnconfiguredProvider()
