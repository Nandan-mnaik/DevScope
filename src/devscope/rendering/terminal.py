from rich.console import Console, Group
from rich.columns import Columns
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from devscope.core.models import ResearchReport

GREEN = "#00FF41"
DIM_GREEN = "#65A765"


def render_report(console: Console, report: ResearchReport, *, watch: bool = False) -> None:
    console.print(_header(report))
    if watch:
        _render_pipeline(console, report)
    console.print(_repositories(report))
    if report.code_evidence:
        console.print(_code_evidence(report))
    console.print(
        Columns(
            [
                Group(_interpretation(report), _landscape(report)),
                Group(_opportunities(report), _recommendations(report)),
            ],
            equal=True,
            expand=True,
            padding=(0, 1),
        )
    )


def _header(report: ResearchReport) -> Group:
    stats = Table.grid(expand=True, padding=(0, 2))
    stats.add_column(justify="center")
    stats.add_column(justify="center")
    stats.add_column(justify="center")
    stats.add_column(justify="center")
    stats.add_row(
        f"[bold {GREEN}]{len(report.repositories)}[/bold {GREEN}]\n[dim]REPOSITORIES[/dim]",
        f"[bold {GREEN}]{len(report.opportunities)}[/bold {GREEN}]\n[dim]OPPORTUNITIES[/dim]",
        f"[bold {GREEN}]{len(report.feature_landscape)}[/bold {GREEN}]\n[dim]FEATURE SIGNALS[/dim]",
        f"[bold {GREEN}]{len(report.recommendation_details) or len(report.recommendations)}[/bold {GREEN}]\n[dim]RECOMMENDATIONS[/dim]",
    )
    return Group(
        Panel(
            "[bold #00FF41]DEV//SCOPE[/bold #00FF41]  [dim]OPEN SOURCE INTELLIGENCE ENGINE[/dim]",
            border_style=GREEN,
            padding=(0, 2),
        ),
        Panel(report.idea, title=f"[bold {GREEN}]TARGET[/bold {GREEN}]", border_style=DIM_GREEN),
        Panel(stats, border_style=DIM_GREEN, padding=(1, 0)),
    )


def _render_pipeline(console: Console, report: ResearchReport) -> None:
    stages = [
        "ANALYZING PROJECT IDEA",
        "GENERATING SEARCH QUERIES",
        "SCANNING GITHUB",
        "FILTERING REPOSITORIES",
        "ANALYZING IMPLEMENTATIONS",
        "BUILDING FEATURE MATRIX",
        "DETECTING OPPORTUNITIES",
        "GENERATING REPORT",
    ]
    table = Table.grid(padding=(0, 2))
    table.add_column(style="dim")
    table.add_column(style="bold #00FF41")
    for index, stage in enumerate(stages, 1):
        status = "COMPLETE" if index <= 5 or report.repositories else "READY"
        table.add_row(f"[{index:02d}/08]", f"{stage:<30} {status}")
    console.print(Panel(table, title="[bold #00FF41]RESEARCH PIPELINE[/bold #00FF41]", border_style=DIM_GREEN))


def _interpretation(report: ResearchReport) -> Panel:
    analysis = report.idea_analysis
    body = Group(
        Text(f"PROBLEM     {analysis.problem}"),
        Text(f"USERS       {', '.join(analysis.target_users)}"),
        Text(f"CAPABILITIES {', '.join(analysis.capabilities)}"),
        Text(f"TECHNOLOGY  {', '.join(analysis.technologies) or 'signal not yet classified'}"),
    )
    return Panel(body, title="[bold #00FF41]IDEA ANALYSIS[/bold #00FF41]", border_style=DIM_GREEN)


def _repositories(report: ResearchReport) -> Table | Panel:
    if not report.repositories:
        return Panel("No repositories discovered. Add GITHUB_TOKEN to enable GitHub discovery.", title="[bold #00FF41]REPOSITORIES[/bold #00FF41]", border_style=DIM_GREEN)
    table = Table(title="REPOSITORIES", border_style=DIM_GREEN, header_style=f"bold {GREEN}")
    table.add_column("SIGNAL", justify="right")
    table.add_column("REPOSITORY")
    table.add_column("LANGUAGE")
    table.add_column("STARS", justify="right")
    for repo in report.repositories:
        repository_link = Text(repo.full_name, style=f"link {repo.url}")
        table.add_row(f"{repo.relevance_score:.0%}", repository_link, repo.language or "-", f"{repo.stars:,}")
    return table


def _landscape(report: ResearchReport) -> Panel:
    features = report.feature_landscape or {"no analyzed features": 0}
    body = "\n".join(f"[bold #00FF41]{count:>3}[/bold #00FF41]  {name}" for name, count in features.items())
    return Panel(body, title="[bold #00FF41]FEATURE LANDSCAPE[/bold #00FF41]", border_style=DIM_GREEN)


def _code_evidence(report: ResearchReport) -> Panel:
    table = Table(border_style=DIM_GREEN, header_style=f"bold {GREEN}")
    table.add_column("REPOSITORY")
    table.add_column("FILE")
    table.add_column("MATCH", justify="right")
    for item in report.code_evidence:
        table.add_row(item.repository, item.path, f"{item.score:.0%}")
    return Panel(table, title=f"[bold {GREEN}]RETRIEVED CODE EVIDENCE[/bold {GREEN}]", border_style=DIM_GREEN)


def _bar(value: int, maximum: int) -> str:
    width = 20
    filled = round((value / maximum) * width) if maximum else 0
    return "[bold #00FF41]" + "#" * filled + "[dim]" + "." * (width - filled) + "[/dim][/bold #00FF41]"


def _recommendations(report: ResearchReport) -> Panel:
    lines = []
    for item in report.recommendation_details:
        lines.extend([f"[bold {GREEN}]{item.priority}[/bold {GREEN}]  {item.action}", item.rationale, f"Benefit: {item.expected_benefit}", f"Evidence: {', '.join(item.evidence) or 'none recorded'}", ""])
    if not lines:
        lines = [f"[bold #00FF41]>[/bold #00FF41] {item}" for item in report.recommendations]
    return Panel("\n".join(lines).rstrip(), title="[bold #00FF41]RECOMMENDATIONS / BETTERMENT[/bold #00FF41]", border_style=DIM_GREEN)


def _opportunities(report: ResearchReport) -> Panel:
    if not report.opportunities:
        return Panel("No opportunities detected yet.", title="[bold #00FF41]OPPORTUNITIES[/bold #00FF41]", border_style=DIM_GREEN)
    lines = []
    for opportunity in report.opportunities:
        evidence = ", ".join(opportunity.evidence) or "none recorded"
        coverage = f"{opportunity.coverage}/{opportunity.total_repositories}"
        lines.extend([f"[bold {GREEN}]{opportunity.title}[/bold {GREEN}]", opportunity.description, f"Coverage {coverage}  {_bar(opportunity.coverage, opportunity.total_repositories)}", f"Confidence {opportunity.confidence:.0%}  |  Difficulty {opportunity.difficulty}  |  Differentiation {opportunity.differentiation_potential}", f"Evidence: {evidence}", ""])
    return Panel("\n".join(lines).rstrip(), title="[bold #00FF41]OPPORTUNITIES / EVIDENCE[/bold #00FF41]", border_style=DIM_GREEN)
