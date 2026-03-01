#!/usr/bin/env python3
"""Build Philippines province-level proxy scores for IUU fishing mentions."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Iterable
from urllib.error import URLError
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
OUTPUT_FILE = DATA_DIR / "iuu_scores.json"

SEARCH_FEEDS = [
    "https://news.google.com/rss/search?q=illegal+fishing+Philippines&hl=en-PH&gl=PH&ceid=PH:en",
    "https://news.google.com/rss/search?q=IUU+fishing+Philippines&hl=en-PH&gl=PH&ceid=PH:en",
]

PROVINCES = [
    "Abra", "Agusan del Norte", "Agusan del Sur", "Aklan", "Albay", "Antique", "Apayao", "Aurora",
    "Basilan", "Bataan", "Batanes", "Batangas", "Benguet", "Biliran", "Bohol", "Bukidnon", "Bulacan",
    "Cagayan", "Camarines Norte", "Camarines Sur", "Camiguin", "Capiz", "Catanduanes", "Cavite", "Cebu",
    "Cotabato", "Davao de Oro", "Davao del Norte", "Davao del Sur", "Davao Occidental", "Davao Oriental",
    "Dinagat Islands", "Eastern Samar", "Guimaras", "Ifugao", "Ilocos Norte", "Ilocos Sur", "Iloilo",
    "Isabela", "Kalinga", "La Union", "Laguna", "Lanao del Norte", "Lanao del Sur", "Leyte", "Maguindanao del Norte",
    "Maguindanao del Sur", "Marinduque", "Masbate", "Misamis Occidental", "Misamis Oriental", "Mountain Province",
    "Negros Occidental", "Negros Oriental", "Northern Samar", "Nueva Ecija", "Nueva Vizcaya", "Occidental Mindoro",
    "Oriental Mindoro", "Palawan", "Pampanga", "Pangasinan", "Quezon", "Quirino", "Rizal", "Romblon", "Samar",
    "Sarangani", "Siquijor", "Sorsogon", "South Cotabato", "Southern Leyte", "Sultan Kudarat", "Sulu", "Surigao del Norte",
    "Surigao del Sur", "Tarlac", "Tawi-Tawi", "Zambales", "Zamboanga del Norte", "Zamboanga del Sur", "Zamboanga Sibugay",
    "Metropolitan Manila",
]

ALIASES = {
    "Metro Manila": "Metropolitan Manila",
    "NCR": "Metropolitan Manila",
    "Manila": "Metropolitan Manila",
    "North Cotabato": "Cotabato",
}

FALLBACK_SNIPPETS = [
    "IUU fishing operations intercepted off Palawan and Occidental Mindoro.",
    "Illegal fishing arrests reported in Zamboanga del Norte and Basilan waters.",
    "Coast guard patrols in Cebu and Bohol increase maritime enforcement.",
    "Small fishers in Quezon and Batangas report losses linked to illegal trawling.",
    "Authorities cite repeated incursions in Sulu and Tawi-Tawi corridors.",
    "Northern waters monitoring highlights Cagayan and Ilocos Norte incidents.",
]


def fetch_text(url: str) -> str:
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=20) as response:
        return response.read().decode("utf-8", errors="ignore")


def parse_rss_items(xml_text: str) -> list[str]:
    root = ET.fromstring(xml_text)
    snippets: list[str] = []
    for item in root.findall(".//item"):
        title = (item.findtext("title") or "").strip()
        desc = (item.findtext("description") or "").strip()
        combined = f"{title} {desc}".strip()
        if combined:
            snippets.append(combined)
    return snippets


def scrape_mentions(urls: Iterable[str]) -> tuple[list[str], list[str]]:
    snippets: list[str] = []
    used_urls: list[str] = []
    for url in urls:
        try:
            xml_text = fetch_text(url)
            snippets.extend(parse_rss_items(xml_text))
            used_urls.append(url)
        except (URLError, ET.ParseError) as exc:
            print(f"[warn] failed to fetch {url}: {exc}")
    return used_urls, snippets


def count_province_mentions(texts: Iterable[str]) -> Counter[str]:
    counts: Counter[str] = Counter({province: 0 for province in PROVINCES})
    patterns = {p: re.compile(rf"\b{re.escape(p)}\b", re.IGNORECASE) for p in PROVINCES}
    alias_patterns = {a: re.compile(rf"\b{re.escape(a)}\b", re.IGNORECASE) for a in ALIASES}

    for text in texts:
        for province, pattern in patterns.items():
            counts[province] += len(pattern.findall(text))
        for alias, pattern in alias_patterns.items():
            counts[ALIASES[alias]] += len(pattern.findall(text))
    return counts


def build_output_payload(counts: Counter[str], sources: list[str], sample_size: int) -> dict:
    max_count = max(counts.values()) if counts else 1
    provinces = []
    for province in sorted(PROVINCES):
        mentions = int(counts[province])
        score = round((mentions / max_count) * 100, 1) if max_count else 0
        provinces.append({"province": province, "mentions": mentions, "iuu_score": score})

    return {
        "country": "Philippines",
        "method": "Province mention counts from IUU-related news RSS snippets (proxy metric)",
        "sources": sources,
        "sample_size": sample_size,
        "provinces": provinces,
    }


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    source_urls, snippets = scrape_mentions(SEARCH_FEEDS)
    if not snippets:
        print("[warn] no remote snippets collected; using fallback seed snippets")
        snippets = FALLBACK_SNIPPETS
        source_urls = ["fallback_seed_data"]

    counts = count_province_mentions(snippets)
    payload = build_output_payload(counts, source_urls, len(snippets))
    OUTPUT_FILE.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    print(f"[ok] wrote {OUTPUT_FILE}")
    print(f"[ok] parsed snippets: {payload['sample_size']}")


if __name__ == "__main__":
    main()
