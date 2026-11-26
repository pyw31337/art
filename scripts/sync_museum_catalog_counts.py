#!/usr/bin/env python3
"""
scripts/sync_museum_catalog_counts.py
Syncs real matched collection counts and sample artworks into data/top_museums_master_catalog.json.
Follows RULE #75 (True Observability / Single Source of Truth).
"""

import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAT_PATH = os.path.join(BASE_DIR, "data", "top_museums_master_catalog.json")
DG_PATH = os.path.join(BASE_DIR, "data", "digital_gallery_master_db.json")
PAINT_PATH = os.path.join(BASE_DIR, "data", "art_paintings_master_db.json")
FED_PATH = os.path.join(BASE_DIR, "data", "federated_open_masterpieces.json")

def sync_catalog():
    with open(CAT_PATH, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    with open(DG_PATH, "r", encoding="utf-8") as f:
        dg = json.load(f)

    with open(PAINT_PATH, "r", encoding="utf-8") as f:
        paint = json.load(f)

    fed = []
    if os.path.exists(FED_PATH):
        try:
            with open(FED_PATH, "r", encoding="utf-8") as f:
                fed = json.load(f)
        except Exception:
            fed = []

    all_arts = (paint.get("featured_masterpieces", []) +
                paint.get("featured_paintings", []) +
                dg.get("artworks", []) +
                fed)

    print(f"[*] Total artworks pool: {len(all_arts)}")

    for m in catalog.get("museums", []):
        m_id = m["id"]
        m_artists = [a.lower().strip() for a in m.get("artists", [])]
        matched = []

        for art in all_arts:
            mus = (art.get("museum") or art.get("location") or art.get("museum_key") or "").lower()
            akr = (art.get("artist_name_kr") or art.get("artist") or "").lower()
            
            is_match = False
            if m_id == 'louvre' and ('루브르' in mus or 'louvre' in mus): is_match = True
            elif m_id == 'moma' and ('moma' in mus or '근대미술관' in mus): is_match = True
            elif m_id == 'met' and ('메트로폴리탄' in mus or 'metropolitan' in mus or 'the met' in mus): is_match = True
            elif m_id == 'orsay' and ('오르세' in mus or 'orsay' in mus): is_match = True
            elif m_id == 'prado' and ('프라도' in mus or 'prado' in mus): is_match = True
            elif m_id == 'uffizi' and ('우피치' in mus or 'uffizi' in mus): is_match = True
            elif m_id == 'national_gallery' and ('내셔널' in mus or 'national gallery' in mus): is_match = True
            elif m_id == 'nmk' and (art.get("museum_key") == "nmk" or '국립중앙박물관' in mus or '간송' in mus or any(k in akr for k in ['김홍도', '정선', '신윤복', '이중섭', '강세황', '김정희'])): is_match = True
            elif m_id == 'rijksmuseum' and ('암스테르담' in mus or 'rijks' in mus): is_match = True
            elif m_id == 'tate' and ('테이트' in mus or 'tate' in mus): is_match = True

            if not is_match and m_artists:
                for art_name in m_artists:
                    if art_name in akr or akr in art_name:
                        is_match = True
                        break

            if is_match:
                matched.append(art.get("id") or art.get("work_id"))

        m["artworks"] = matched
        m["matched_works_count"] = len(matched)
        print(f"  - {m['name_kr']} ({m_id}): {len(matched)} works linked")

    with open(CAT_PATH, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)

    print(f"[+] Updated {CAT_PATH} with genuine matched artwork IDs!")

if __name__ == "__main__":
    sync_catalog()
