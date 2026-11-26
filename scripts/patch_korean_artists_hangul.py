#!/usr/bin/env python3
"""
scripts/patch_korean_artists_hangul.py
Enriches Korean master artists in digital_gallery_master_db.json:
Maps Hanja artist names (金弘道, 鄭歚, 申潤福 등) to clear Hangul names,
stores Hanja in artist_name_hanja, and sets proper museum attribution.
"""

import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "digital_gallery_master_db.json")

HANJA_MAP = {
    "金弘道": "김홍도",
    "鄭歚": "정선",
    "姜世晃": "강세황",
    "安中植": "안중식",
    "李仲燮": "이중섭",
    "金奎鎭": "김규진",
    "申潤福": "신윤복",
    "池雲英": "지운영",
    "李用雨": "이용우",
    "金得臣": "김득신",
    "崔北": "최북",
    "李寅文": "이인문",
    "金正喜": "김정희",
    "李在寬": "이재관",
    "羅蕙錫": "나혜석",
    "金允謙": "김윤겸",
    "金應煥": "김응환",
    "劉淑": "유숙",
    "姜熙彦": "강희언"
}

def patch_database():
    with open(DB_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)

    artworks = db.get("artworks", [])
    updated = 0

    for a in artworks:
        raw_name = a.get("artist_name_kr", "")
        if raw_name in HANJA_MAP:
            hangul_name = HANJA_MAP[raw_name]
            a["artist_name_hanja"] = raw_name
            a["artist_name_kr"] = hangul_name
            # If museum is generic ECO, also specify National Museum / Kansong heritage
            if a.get("museum") == "이씨오 디지털 갤러리 (ECO Digital Gallery)":
                a["museum_detail"] = "국립중앙박물관 & 간송미술관 소장 고미술 컬렉션"
                a["museum_key"] = "nmk"
            updated += 1

    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print(f"[+] Successfully patched {updated} Korean artworks with Hangul names and NMK museum key!")

if __name__ == "__main__":
    patch_database()
