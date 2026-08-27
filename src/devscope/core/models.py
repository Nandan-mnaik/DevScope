from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class IdeaAnalysis(BaseModel):
    problem: str
    target_users: list[str] = Field(default_factory=list)
    capabilities: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    domain: str = "software development"
    architecture_concepts: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    synonyms: list[str] = Field(default_factory=list)


class SearchQuery(BaseModel):
    query: str
    strategy: str


class Repository(BaseModel):
    full_name: str
    url: str
    description: str | None = None
    language: str | None = None
    stars: int = 0
    forks: int = 0
    updated_at: str | None = None
    relevance_score: float = 0.0
    relevance_reasons: list[str] = Field(default_factory=list)


class RepositoryFingerprint(BaseModel):
    repository: str
    language: str | None = None
    frameworks: list[str] = Field(default_factory=list)
    architecture: list[str] = Field(default_factory=list)
    databases: list[str] = Field(default_factory=list)
    llm_providers: list[str] = Field(default_factory=list)
    features: list[str] = Field(default_factory=list)
    integrations: list[str] = Field(default_factory=list)
    deployment: list[str] = Field(default_factory=list)
    mcp: bool = False


class RepositoryAnalysis(BaseModel):
    repository: Repository
    fingerprint: RepositoryFingerprint
    evidence: list[str] = Field(default_factory=list)


class Opportunity(BaseModel):
    title: str
    description: str
    coverage: int
    total_repositories: int
    evidence: list[str]
    confidence: float = Field(ge=0, le=1)
    difficulty: str
    differentiation_potential: str
    supporting_repositories: list[str] = Field(default_factory=list)


class Recommendation(BaseModel):
    action: str
    rationale: str
    evidence: list[str] = Field(default_factory=list)
    expected_benefit: str
    priority: str


class CodeEvidence(BaseModel):
    repository: str
    path: str
    content: str
    score: float = 0.0


class Comparison(BaseModel):
    common_technologies: list[str] = Field(default_factory=list)
    common_architectures: list[str] = Field(default_factory=list)
    common_features: list[str] = Field(default_factory=list)
    rare_features: list[str] = Field(default_factory=list)
    missing_features: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class ResearchReport(BaseModel):
    idea: str
    idea_analysis: IdeaAnalysis
    search_queries: list[SearchQuery]
    repositories: list[Repository] = Field(default_factory=list)
    repository_analyses: list[RepositoryAnalysis] = Field(default_factory=list)
    technology_landscape: dict[str, int] = Field(default_factory=dict)
    feature_landscape: dict[str, int] = Field(default_factory=dict)
    comparison: Comparison = Field(default_factory=Comparison)
    gaps: list[str] = Field(default_factory=list)
    opportunities: list[Opportunity] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    recommendation_details: list[Recommendation] = Field(default_factory=list)
    code_evidence: list[CodeEvidence] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def to_markdown(self) -> str:
        lines = [f"# DEV//SCOPE Research Report\n\n## Target\n{self.idea}", "\n## Interpretation", self.idea_analysis.model_dump_json(indent=2)]
        lines += ["\n## Search Queries", *[f"- **{item.strategy}**: `{item.query}`" for item in self.search_queries]]
        lines += ["\n## Relevant Repositories", *[f"- [{repo.full_name}]({repo.url}) - {repo.relevance_score:.0%} heuristic relevance" for repo in self.repositories]]
        lines += ["\n## Landscape", *[f"- {name}: {count}/{len(self.repositories)} repositories" for name, count in self.feature_landscape.items()], "\n## Comparison", f"Common technologies: {', '.join(self.comparison.common_technologies) or 'none detected'}", f"Common features: {', '.join(self.comparison.common_features) or 'none detected'}", f"Rare features: {', '.join(self.comparison.rare_features) or 'none detected'}"]
        lines += ["\n## Opportunities", *[f"### {item.title}\n{item.description}\n\nCoverage: {item.coverage}/{item.total_repositories} | Confidence: {item.confidence:.0%} | Difficulty: {item.difficulty} | Differentiation: {item.differentiation_potential}\n\nEvidence: {', '.join(item.evidence)}" for item in self.opportunities]]
        lines += ["\n## Recommendations", *[f"### {item.priority}: {item.action}\n{item.rationale}\n\nExpected benefit: {item.expected_benefit}\n\nEvidence: {', '.join(item.evidence) or 'none recorded'}" for item in self.recommendation_details]]
        return "\n".join(lines) + "\n"

    def to_rich(self) -> str:
        return self.to_markdown()

    @staticmethod
    def timestamp() -> str:
        return datetime.now(timezone.utc).isoformat()
