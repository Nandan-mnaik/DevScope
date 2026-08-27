# DEV//SCOPE

DevScope is a CLI-first research instrument for developers. It investigates open-source implementations before development and produces evidence-backed comparisons, gaps, and differentiation opportunities.

## Quick start

```powershell
pip install -e .
devscope init
devscope research "An MCP-powered AI research agent"
```

GitHub access is optional. DevScope uses `GITHUB_TOKEN` when present, then reuses an existing GitHub CLI login, then falls back to unauthenticated public API access. For the best rate limits without managing an environment token, run `gh auth login` first.

To let DevScope ask you to connect your own GitHub account:

```powershell
devscope auth github
```

This opens GitHub's browser/device login through the GitHub CLI. DevScope reads the resulting local CLI session; no `GITHUB_TOKEN` needs to be placed in `.env`.

## Free local LLM for MCP

DevScope defaults to Ollama, so no paid provider or API key is required. Install Ollama, then pull a model:

```powershell
ollama pull qwen2.5:7b
devscope mcp
```

DevScope uses Qwen 2.5 7B by default because it is more reliable at structured JSON and multi-step analysis than the smaller starter model. Use `OLLAMA_BASE_URL`, `LLM_MODEL`, and `LLM_PROVIDER` in `.env` to select another locally served Ollama model. Repository content should always be treated as untrusted source material by the model.

For a GitHub-hosted option, set `LLM_PROVIDER=github-models`, set `LLM_MODEL` to a model available to your GitHub account, and provide `GITHUB_TOKEN`. This uses GitHub Models rather than an undocumented Copilot endpoint. Copilot-specific API access can be added later if GitHub exposes an official SDK contract for standalone MCP servers.

## Gemini with Google login

Use Gemini through Vertex AI without putting a Google API key in `.env`:

```powershell
devscope auth google --project YOUR_GOOGLE_CLOUD_PROJECT
```

This opens Google login through the Google Cloud CLI and stores short-lived credentials in Google's local application-default credential store. The project must have Vertex AI enabled and billing/quota configured. A normal consumer Google account login by itself is not enough for hosted Gemini API access. After login, both `devscope research ...` and `devscope mcp` use Gemini when `LLM_PROVIDER=gemini`.
