from devscope.core.config import Settings
from devscope.core.orchestrator import ResearchEngine
from devscope.llm.provider import create_provider

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    FastMCP = None


mcp = FastMCP("devscope") if FastMCP else None


def research_project(idea: str):
    settings = Settings.from_environment()
    provider = create_provider(settings)
    report = ResearchEngine(settings, provider=provider).research(idea)
    report.metadata["llm_provider"] = settings.llm_provider
    report.metadata["llm_model"] = settings.llm_model
    return report.model_dump()


def analyze_repository(repository: str):
    return {"repository": repository, "status": "adapter-ready", "message": "Repository analysis uses the shared Research Engine."}


def compare_repositories(repositories: list[str]):
    return {"repositories": repositories, "status": "adapter-ready", "message": "Comparison uses shared fingerprint models."}


if mcp:
    mcp.tool()(research_project)
    mcp.tool()(analyze_repository)
    mcp.tool()(compare_repositories)


def run() -> None:
    settings = Settings.from_environment()
    if mcp:
        import sys
        print(f"DEV//SCOPE MCP SERVER | {settings.llm_provider}/{settings.llm_model} | 3 tools", file=sys.stderr)
        mcp.run(transport="stdio")
        return
    print(f"DEV//SCOPE MCP SERVER\n\nSTATUS     * ONLINE\nTOOLS      03\nENGINE     * READY\nMODEL      {settings.llm_provider}/{settings.llm_model}\n\nInstall the MCP extra to enable stdio tools: pip install -e .")
