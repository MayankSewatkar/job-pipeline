"""
Pulls jobs from Greenhouse's public job board API.
No API key needed. Works for any company using Greenhouse with a public board,
e.g. boards.greenhouse.io/<token>

Find a company's token by visiting their careers page — if it's Greenhouse,
the URL or embedded iframe will contain boards.greenhouse.io/<token>.
"""
import requests

API_URL = "https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"


def fetch(token: str) -> list[dict]:
    """Fetch all open jobs for a single Greenhouse board token."""
    resp = requests.get(API_URL.format(token=token), timeout=20)
    if resp.status_code != 200:
        print(f"[greenhouse] {token}: HTTP {resp.status_code}, skipping")
        return []

    payload = resp.json()
    jobs = []
    for job in payload.get("jobs", []):
        jobs.append({
            "id": f"greenhouse-{token}-{job['id']}",
            "title": job.get("title", "").strip(),
            "company": token.replace("-", " ").title(),
            "location": (job.get("location") or {}).get("name", ""),
            "url": job.get("absolute_url", ""),
            "source": "greenhouse",
            "posted_at": job.get("updated_at"),
            "salary": None,
            "description_snippet": _strip_html(job.get("content", ""))[:400],
        })
    return jobs


def _strip_html(raw: str) -> str:
    import re
    text = re.sub(r"<[^>]+>", " ", raw or "")
    return re.sub(r"\s+", " ", text).strip()


def fetch_all(tokens: list[str]) -> list[dict]:
    all_jobs = []
    for token in tokens:
        all_jobs.extend(fetch(token))
    return all_jobs
