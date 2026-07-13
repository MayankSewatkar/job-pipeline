"""
Pulls jobs from Lever's public postings API.
No API key needed. Works for any company using Lever with a public board,
e.g. jobs.lever.co/<company>
"""
import requests

API_URL = "https://api.lever.co/v0/postings/{company}?mode=json"


def fetch(company: str) -> list[dict]:
    resp = requests.get(API_URL.format(company=company), timeout=20)
    if resp.status_code != 200:
        print(f"[lever] {company}: HTTP {resp.status_code}, skipping")
        return []

    jobs = []
    for job in resp.json():
        categories = job.get("categories", {})
        jobs.append({
            "id": f"lever-{company}-{job['id']}",
            "title": job.get("text", "").strip(),
            "company": company.replace("-", " ").title(),
            "location": categories.get("location", ""),
            "url": job.get("hostedUrl", ""),
            "source": "lever",
            "posted_at": _epoch_to_iso(job.get("createdAt")),
            "salary": _extract_salary(job),
            "description_snippet": _strip_html(job.get("descriptionPlain") or job.get("description", ""))[:400],
        })
    return jobs


def _epoch_to_iso(ms):
    if not ms:
        return None
    from datetime import datetime, timezone
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).isoformat()


def _extract_salary(job: dict):
    # Lever sometimes includes salary in a structured field, sometimes not at all.
    salary_range = job.get("salaryRange")
    if salary_range:
        return salary_range
    return None


def _strip_html(raw: str) -> str:
    import re
    text = re.sub(r"<[^>]+>", " ", raw or "")
    return re.sub(r"\s+", " ", text).strip()


def fetch_all(companies: list[str]) -> list[dict]:
    all_jobs = []
    for company in companies:
        all_jobs.extend(fetch(company))
    return all_jobs
