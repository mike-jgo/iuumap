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

### macOS / Linux

```bash
python3 scripts/scrape_iuu_data.py
python3 -m http.server 8000
```

Open `http://localhost:8000/web/`.

### Windows (PowerShell / CMD)

```powershell
py scripts\scrape_iuu_data.py
py -m http.server 8000
```

Open `http://localhost:8000/web/`.

## If Python is not found on Windows

If you see:

- `Python was not found; run without arguments to install from the Microsoft Store...`

use one of these fixes:

1. Install Python from `https://www.python.org/downloads/windows/` and enable **Add python.exe to PATH** during install.
2. Or use the `py` launcher commands shown above.
3. If Store alias keeps interfering, disable **App execution aliases** for Python in Windows Settings.

## Data quality improvements

- Add more Philippines-specific sources (government bulletins, BFAR advisories, court records, NGO reports).
- Add time decay weighting for recent incidents.
- Replace mention-count proxy with verified incident-level province records.
