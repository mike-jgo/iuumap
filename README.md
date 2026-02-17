# Philippines IUU Fishing Province Choropleth

This project creates a **province-level choropleth** for the **Philippines only**, showing which provinces are more affected by IUU (Illegal, Unreported, and Unregulated) fishing using a proxy metric.

## Workflow

1. Scrape IUU-related news RSS feeds that target the Philippines.
2. Count province-name mentions in snippets/titles.
3. Convert mention counts into normalized `iuu_score` values.
4. Render scores on a Philippines province map.

> This is a proxy indicator and should not be treated as official enforcement statistics.

## Project structure

- `scripts/scrape_iuu_data.py` – scraper + province scoring (Philippines-only).
- `data/iuu_scores.json` – generated scores.
- `web/index.html` – Leaflet choropleth map.

## Run

```bash
python3 scripts/scrape_iuu_data.py
python3 -m http.server 8000
```

Open `http://localhost:8000/web/`.

## Data quality improvements

- Add more Philippines-specific sources (government bulletins, BFAR advisories, court records, NGO reports).
- Add time decay weighting for recent incidents.
- Replace mention-count proxy with verified incident-level province records.
