#!/usr/bin/env bash
# Runs the scraper (optional) then serves the dashboard locally at http://localhost:8000
set -e
cd "$(dirname "$0")/.."

if [ "$1" == "--scrape" ]; then
  echo "Running scraper..."
  pip install -q -r requirements.txt
  python -m scraper.main
fi

mkdir -p dashboard/data
cp data/jobs.json dashboard/data/jobs.json

echo "Serving dashboard at http://localhost:8000"
cd dashboard && python3 -m http.server 8000
