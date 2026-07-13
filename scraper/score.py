"""
Scores each job 0-100 against data/config.json targets, then assigns a tier.

This is a simple weighted keyword matcher for now. It's intentionally
readable/tweakable rather than clever, since the real scoring logic
(rules vs. an LLM call vs. a hybrid) is still TBD.

Weights sum to 100:
  - title match against target positions:   40
  - company in target company list:         20
  - level keyword match:                    15
  - industry keyword match (description):   15
  - location match:                         10
"""
import re


def _normalize(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip().lower()


def _fuzzy_contains(haystack: str, needle: str) -> bool:
    haystack, needle = _normalize(haystack), _normalize(needle)
    if not needle:
        return False
    return needle in haystack or all(word in haystack for word in needle.split())


def score_job(job: dict, targets: dict) -> int:
    score = 0
    title = job.get("title", "")
    company = job.get("company", "")
    location = job.get("location", "")
    description = job.get("description_snippet", "")

    # Title vs target positions (40 pts)
    positions = targets.get("positions", [])
    if positions and any(_fuzzy_contains(title, p) for p in positions):
        score += 40

    # Company match (20 pts)
    companies = targets.get("companies", [])
    if companies and any(_fuzzy_contains(company, c) for c in companies):
        score += 20

    # Level match (15 pts) — check title + description
    levels = targets.get("levels", [])
    if levels and any(_fuzzy_contains(title, lvl) or _fuzzy_contains(description, lvl) for lvl in levels):
        score += 15

    # Industry match (15 pts) — description only, since it's rarely in the title
    industries = targets.get("industries", [])
    if industries and any(_fuzzy_contains(description, ind) for ind in industries):
        score += 15

    # Location match (10 pts)
    locations = targets.get("locations", [])
    if locations and any(_fuzzy_contains(location, loc) for loc in locations):
        score += 10

    return min(score, 100)


def tier_for_score(score: int, scoring_cfg: dict) -> int:
    if score >= scoring_cfg.get("tier1_min", 85):
        return 1
    if score >= scoring_cfg.get("tier2_min", 65):
        return 2
    return 3
