from typing import Any
import base64
import httpx
import shutil
import subprocess


class GitHubError(RuntimeError):
    pass


class GitHubClient:
    def __init__(self, token: str | None = None, timeout: float = 20.0):
        token = token or self._gh_token()
        headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self.client = httpx.Client(base_url="https://api.github.com", headers=headers, timeout=timeout)

    @staticmethod
    def _gh_token() -> str | None:
        """Reuse GitHub CLI credentials without copying secrets into .env."""
        if not shutil.which("gh"):
            return None
        try:
            result = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, timeout=5, check=False)
        except (OSError, subprocess.SubprocessError):
            return None
        token = result.stdout.strip()
        return token or None

    def request(self, path: str, **params: Any) -> Any:
        response = self.client.get(path, params=params)
        if response.status_code == 401:
            raise GitHubError("GitHub authentication failed. Run: devscope auth github")
        if response.status_code == 403:
            raise GitHubError("GitHub rate limit reached. Run `gh auth login` or set GITHUB_TOKEN.")
        if response.is_error:
            raise GitHubError(f"GitHub API error ({response.status_code}): {response.text[:200]}")
        return response.json()

    def search_repositories(self, query: str, limit: int = 30) -> list[dict[str, Any]]:
        qualified_query = f"{query} in:name,description"
        return self.request("/search/repositories", q=qualified_query, per_page=min(limit, 100)).get("items", [])

    def repository(self, full_name: str) -> dict[str, Any]:
        return self.request(f"/repos/{full_name}")

    def readme(self, full_name: str) -> str:
        response = self.client.get(f"/repos/{full_name}/readme", headers={"Accept": "application/vnd.github.raw+json"})
        if response.status_code == 404:
            return ""
        response.raise_for_status()
        return response.text

    def tree(self, full_name: str) -> list[dict[str, Any]]:
        repository = self.repository(full_name)
        data = self.request(f"/repos/{full_name}/git/trees/{repository.get('default_branch', 'main')}", recursive="1")
        return data.get("tree", [])

    def source_files(self, full_name: str, *, max_files: int = 12, max_bytes: int = 12000) -> list[dict[str, str]]:
        """Fetch bounded text files so indexing cannot consume an entire repository."""
        allowed = {".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".rb", ".php", ".cs", ".md", ".yaml", ".yml", ".toml"}
        files = []
        for item in self.tree(full_name):
            path = item.get("path", "")
            if item.get("type") != "blob" or not any(path.lower().endswith(extension) for extension in allowed):
                continue
            if any(part in path.lower().split("/") for part in ("node_modules", ".git", "dist", "build", "vendor", "__pycache__")):
                continue
            try:
                data = self.request(f"/repos/{full_name}/git/blobs/{item['sha']}")
                content = base64.b64decode(data.get("content", "")).decode("utf-8", errors="ignore")[:max_bytes]
            except (KeyError, ValueError, UnicodeError, GitHubError):
                continue
            if content.strip():
                files.append({"path": path, "content": content})
            if len(files) >= max_files:
                break
        return files
