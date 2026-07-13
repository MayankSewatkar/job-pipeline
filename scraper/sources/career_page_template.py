"""
Template for companies with no public Greenhouse/Lever API (e.g. JPMorgan,
most large enterprises with in-house career sites).

These need a dedicated scraper per site because HTML structure varies.
Copy this file to something like `jpmorgan.py`, fill in the selectors,
and register it in scraper/main.py.

This template deliberately does nothing destructive — it returns an empty
list until you wire in real selectors, so main.py won't break if you add
a career_pages entry to config.json before writing the scraper.
"""
import requests
from bs4 import BeautifulSoup


def fetch(url: str, company: str) -> list[dict]:
    try:
        resp = requests.get(url, timeout=20, headers={
            "User-Agent": "Mozilla/5.0 (compatible; job-pipeline-bot/1.0)"
        })
    except requests.RequestException as e:
        print(f"[career_page:{company}] request failed: {e}")
        return []

    if resp.status_code != 200:
        print(f"[career_page:{company}] HTTP {resp.status_code}, skipping")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")

    # --- FILL THIS IN PER COMPANY ---
    # Example pattern once you inspect the page's HTML:
    #
    # cards = soup.select(".job-card")
    # jobs = []
    # for card in cards:
    #     jobs.append({
    #         "id": f"career-{company}-{card['data-job-id']}",
    #         "title": card.select_one(".job-title").get_text(strip=True),
    #         "company": company,
    #         "location": card.select_one(".job-location").get_text(strip=True),
    #         "url": card.select_one("a")["href"],
    #         "source": "career_page",
    #         "posted_at": None,
    #         "salary": None,
    #         "description_snippet": "",
    #     })
    # return jobs

    print(f"[career_page:{company}] selectors not implemented yet — returning 0 jobs")
    return []
