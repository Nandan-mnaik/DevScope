from devscope.core.models import Repository


def rank_repositories(items: list[dict], keywords: list[str]) -> list[Repository]:
    ranked = []
    agent_intent = any(term in keywords for term in ("agent", "coding agent", "ai coding agent", "software engineering agent"))
    for item in items:
        text = f"{item.get('name', '')} {item.get('description', '')}".lower()
        concept_terms = {"ai", "coding", "code", "agent", "developer", "software", "engineering", "generation", "assistant", "terminal", "repository", "cursor"}
        meaningful = [word for word in keywords if word in concept_terms or " " in word]
        overlap = sum(1 for word in meaningful if word in text)
        domain_hits = sum(term in text for term in ("code", "coding", "developer", "software", "programming", "repository"))
        agent_hits = sum(term in text for term in ("agent", "assistant", "copilot", "llm", "language model", "codegen", "code generation"))
        if agent_intent and (domain_hits == 0 or agent_hits == 0):
            continue
        if agent_intent and "website" in text and "clone" in text:
            continue
        score = min(0.99, 0.15 + overlap * 0.12 + domain_hits * 0.08 + min(item.get("stargazers_count", 0), 10000) / 100000)
        ranked.append(Repository(full_name=item["full_name"], url=item["html_url"], description=item.get("description"), language=item.get("language"), stars=item.get("stargazers_count", 0), forks=item.get("forks_count", 0), updated_at=item.get("updated_at"), relevance_score=score, relevance_reasons=[f"{overlap} keyword matches", "activity and popularity signals"]))
    return sorted(ranked, key=lambda item: item.relevance_score, reverse=True)
