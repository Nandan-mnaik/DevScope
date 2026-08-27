from pathlib import Path
import shutil
import subprocess

import typer
from rich.console import Console

app = typer.Typer(help="Evidence-backed open source intelligence for developers.", no_args_is_help=True)
repo_app = typer.Typer(help="Analyze a GitHub repository.")
compare_app = typer.Typer(help="Compare repositories.")
report_app = typer.Typer(help="Manage saved research reports.")
auth_app = typer.Typer(help="Authenticate external services.")
app.add_typer(repo_app, name="repo")
app.add_typer(compare_app, name="compare")
app.add_typer(report_app, name="report")
app.add_typer(auth_app, name="auth")
console = Console()


@app.command()
def init() -> None:
    """Create a local .env configuration template."""
    target = Path.cwd() / ".env"
    if target.exists():
        console.print("[yellow]Configuration already exists:[/yellow] .env")
        return
    target.write_text(
        "GITHUB_TOKEN=\nLLM_PROVIDER=ollama\nLLM_API_KEY=\nLLM_MODEL=qwen2.5:7b\n"
        "OLLAMA_BASE_URL=http://127.0.0.1:11434\nGITHUB_MODELS_BASE_URL=https://models.inference.ai.azure.com\n"
        "GOOGLE_CLOUD_PROJECT=\nGOOGLE_CLOUD_LOCATION=us-central1\n"
        "RESEARCH_DEPTH=standard\nREPOSITORY_LIMIT=10\n",
        encoding="utf-8",
    )
    console.print("[green]Initialized DEV//SCOPE configuration in .env[/green]")


@auth_app.command("github")
def auth_github() -> None:
    """Sign in with the user's GitHub account using GitHub CLI."""
    if not shutil.which("gh"):
        raise typer.BadParameter("GitHub CLI is required. Install it from https://cli.github.com/ and retry.")
    console.print("[bold #00FF41]Opening GitHub authentication...[/bold #00FF41]")
    result = subprocess.run(["gh", "auth", "login", "--hostname", "github.com", "--web", "--git-protocol", "https"], check=False)
    if result.returncode:
        raise typer.Exit(result.returncode)
    console.print("[green]GitHub account connected. DevScope will reuse this session.[/green]")


@auth_app.command("google")
def auth_google(project: str = typer.Option(..., "--project", help="Google Cloud project ID with Vertex AI enabled.")) -> None:
    """Sign in with Google for Gemini through Vertex AI."""
    if not shutil.which("gcloud"):
        raise typer.BadParameter("Google Cloud CLI is required. Install it from https://cloud.google.com/sdk/docs/install and retry.")
    console.print("[bold #00FF41]Opening Google authentication...[/bold #00FF41]")
    result = subprocess.run(["gcloud", "auth", "application-default", "login"], check=False)
    if result.returncode:
        raise typer.Exit(result.returncode)
    target = Path.cwd() / ".env"
    existing = target.read_text(encoding="utf-8") if target.exists() else ""
    lines = [line for line in existing.splitlines() if not line.startswith(("LLM_PROVIDER=", "LLM_MODEL=", "GOOGLE_CLOUD_PROJECT="))]
    lines.extend(["LLM_PROVIDER=gemini", "LLM_MODEL=gemini-2.5-flash", f"GOOGLE_CLOUD_PROJECT={project}"])
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    console.print(f"[green]Google account connected. Gemini configured for project {project}.[/green]")


@app.command()
def research(
    idea: str = typer.Argument(None, help="Project idea to investigate."),
    file: Path | None = typer.Option(None, "--file", help="Read the project idea from a file."),
    output_json: bool = typer.Option(False, "--json", help="Emit machine-readable JSON."),
    markdown: bool = typer.Option(False, "--markdown", help="Emit a Markdown report."),
    output: Path | None = typer.Option(None, "--output", help="Write formatted output to a file."),
    depth: str = typer.Option("standard", help="Analysis depth: quick, standard, or deep."),
    limit: int = typer.Option(10, min=1, max=100, help="Maximum repositories to analyze."),
    no_cache: bool = typer.Option(False, "--no-cache", help="Ignore cached API responses."),
    watch: bool = typer.Option(False, "--watch", help="Show live pipeline progress."),
) -> None:
    """Research a project idea across GitHub implementations."""
    from devscope.core.orchestrator import ResearchEngine
    from devscope.core.config import Settings
    from devscope.llm.provider import create_provider

    if file:
        idea = file.read_text(encoding="utf-8").strip()
    if not idea:
        raise typer.BadParameter("Provide an idea argument or --file.")
    if depth not in {"quick", "standard", "deep"}:
        raise typer.BadParameter("Depth must be quick, standard, or deep.")
    settings = Settings.from_environment()
    provider = create_provider(settings)
    report = ResearchEngine(settings, provider=provider).research(
        idea, depth=depth, limit=limit, use_cache=not no_cache, watch=watch
    )
    if output_json:
        rendered = report.model_dump_json(indent=2)
    elif markdown:
        rendered = report.to_markdown()
    else:
        from devscope.rendering.terminal import render_report
        render_report(console, report, watch=watch)
        return
    if output:
        output.write_text(rendered, encoding="utf-8")
        console.print(f"[green]Report written to[/green] {output}")
    else:
        typer.echo(rendered)


@repo_app.command("analyze")
def analyze_repo(repository: str) -> None:
    """Inspect repository metadata and print a compact analysis."""
    from devscope.core.config import Settings
    from devscope.github.client import GitHubClient
    data = GitHubClient(Settings.from_environment().github_token).repository(repository)
    console.print_json(data=data)


@compare_app.callback(invoke_without_command=True)
def compare(repositories: list[str] = typer.Argument(...)) -> None:
    """Compare two or more repositories."""
    if len(repositories) < 2:
        raise typer.BadParameter("Provide at least two repositories.")
    typer.echo(f"Comparison requested for {', '.join(repositories)}; use research reports for evidence-backed fingerprints.")


@report_app.command("list")
def list_reports() -> None:
    """List locally stored reports."""
    from devscope.core.config import Settings
    from devscope.storage.database import Database
    for report_id, idea, created_at in Database(Settings.from_environment().data_dir / "devscope.db").list_reports():
        typer.echo(f"{report_id}\t{created_at}\t{idea}")


@app.command()
def mcp() -> None:
    """Run the MCP integration server."""
    from devscope.mcp.server import run
    run()


@app.callback()
def version() -> None:
    """DEV//SCOPE command line interface."""


if __name__ == "__main__":
    app()
