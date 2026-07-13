"""
Entry point. Run with: python -m scraper.main

1. Loads data/config.json (your target positions/companies/levels/pay/industries)
2. Pulls jobs from every configured source
3. Scores + tiers each job against your targets
4. Merges into data/jobs.json, preserving any status you've already set
   (pending_review / applied / rejected) so re-running never clobbers your progress
"""
import json
from datetime import datetime, timezone
from pathlib import Path

from scraper.sources import greenhouse, lever, career_page_template
from scraper.score import score_job, tier_for_score

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "data" / "config.json"
JOBS_PATH = ROOT / "data" / "jobs.json"


def load_json(path: Path) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def save_json(path: Path, data: dict) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def collect_jobs(config: dict) -> list[dict]:
    sources = config.get("sources", {})
    jobs = []

    jobs.extend(greenhouse.fetch_all(sources.get("greenhouse_boards", [])))
    jobs.extend(lever.fetch_all(sources.get("lever_companies", [])))

    for entry in sources.get("career_pages", []):
        jobs.extend(career_page_template.fetch(entry["url"], entry["company"]))

    return jobs


def main():
    config = load_json(CONFIG_PATH)
    existing = load_json(JOBS_PATH) if JOBS_PATH.exists() else {"last_scraped": None, "jobs": []}
    existing_by_id = {j["id"]: j for j in existing.get("jobs", [])}

    scraped = collect_jobs(config)
    now = datetime.now(timezone.utc).isoformat()

    merged = []
    for job in scraped:
        job["score"] = score_job(job, config["targets"])
        job["tier"] = tier_for_score(job["score"], config["scoring"])
        job["scraped_at"] = now

        prior = existing_by_id.get(job["id"])
        job["status"] = prior["status"] if prior else "pending_review"
        merged.append(job)

    # Keep prior jobs that didn't show up in this scrape (e.g. source hiccup,
    # or you're tracking a job manually) rather than silently dropping them.
    merged_ids = {j["id"] for j in merged}
    for prior_job in existing.get("jobs", []):
        if prior_job["id"] not in merged_ids and prior_job.get("id") != "sample-1":
            merged.append(prior_job)

    merged.sort(key=lambda j: j.get("score", 0), reverse=True)

    save_json(JOBS_PATH, {"last_scraped": now, "jobs": merged})
    print(f"Scraped {len(scraped)} jobs, {len(merged)} total after merge.")


if __name__ == "__main__":
    main()
