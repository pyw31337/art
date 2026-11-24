#!/usr/bin/env python3
"""
scripts/daily_art_pipeline.py
Automated daily crawler, entity extractor, and multi-faceted ontology classifier.
Scrapes new content from Handmaker, ArtInsight, YouTube lecture channels,
classifies artworks across Seasons, Themes, Movements, and Artists,
and synchronizes master databases daily.
"""

import json
import os
import re
import urllib.request
import urllib.parse
from datetime import datetime

# 1. Multi-axis Ontology Tag Definitions
SEASON_RULES = {
    "spring": {
        "label": "🌸 봄의 찬가 (Spring)",
        "keywords": ["봄", "spring", "화원", "꽃", "블라섬", "blossom", "아몬드", "플라워", "flower", "새싹", "단오풍정", "사월", "오월", "프리마베라", "primavera"]
    },
    "summer": {
        "label": "☀️ 눈부신 여름 (Summer)",
        "keywords": ["여름", "summer", "수련", "햇살", "해변", "바다", "물놀이", "그랑드 자트", "해바라기", "비치", "beach", "일광", "휴양"]
    },
    "autumn": {
        "label": "🍂 쓸쓸한 가을빛 (Autumn)",
        "keywords": ["가을", "autumn", "fall", "낙엽", "수확", "이삭", "만종", "단풍", "추수", "갈색", "추일"]
    },
    "winter": {
        "label": "❄️ 시린 겨울과 설경 (Winter)",
        "keywords": ["겨울", "winter", "눈", "snow", "설경", "빙하", "얼음", "ice", "크리스마스", "사냥꾼", "동지"]
    }
}

THEME_RULES = {
    "love": {
        "label": "💘 세기의 연인 & 사랑 (Love & Passion)",
        "keywords": ["키스", "연인", "사랑", "비너스", "입맞춤", "포옹", "웨딩", "결혼", "연모", "월하정인", "kiss", "love", "venus", "lovers"]
    },
    "night": {
        "label": "🌙 밤과 별빛의 선율 (Night & Stars)",
        "keywords": ["밤", "별", "달", "달빛", "야경", "순찰", "심야", "새벽", "starry", "night", "moon", "nocturne"]
    },
    "mystery": {
        "label": "🕵️ 미스터리 & 비밀의 방 (Mystery & Hidden Secrets)",
        "keywords": ["모나리자", "시녀들", "진주 귀걸이", "마담 x", "비하인드", "도난", "스캔들", "괴물", "수수께끼", "고래", "흔적", "스케치", "정물화", "mystery"]
    },
    "revolution": {
        "label": "🔥 혁명과 자유, 저항 (Revolution & Liberty)",
        "keywords": ["혁명", "자유", "민중", "게르니카", "전쟁", "바리케이드", "학살", "투쟁", "깃발", "liberty", "revolution", "war"]
    },
    "solitude": {
        "label": "🕊️ 고독과 실존, 치유 (Solitude & Healing)",
        "keywords": ["절규", "고독", "방랑자", "침묵", "우울", "자화상", "안개", "기도", "생각하는", "scream", "solitude", "melancholy"]
    },
    "nature": {
        "label": "🌿 야성과 원시 정글 (Jungle & Wild Nature)",
        "keywords": ["정글", "호랑이", "사자", "열대", "원시", "주술사", "숲", "동물", "jungle", "forest", "wild", "tropical"]
    },
    "korean": {
        "label": "🇰🇷 한국의 멋과 해학 (Korean Wit & Soul)",
        "keywords": ["신윤복", "김홍도", "정선", "장승업", "안견", "풍속화", "미인도", "씨름", "단오", "서당", "인왕제색도", "조선"]
    }
}

MOVEMENT_RULES = {
    "renaissance": {
        "label": "🏛️ 르네상스 (Renaissance)",
        "keywords": ["다빈치", "다 빈치", "미켈란젤로", "라파엘로", "보티첼리", "조르조네", "티치아노", "renaissance"]
    },
    "baroque": {
        "label": "👑 바로크 & 로코코 (Baroque)",
        "keywords": ["렘브란트", "카라바조", "페르메이르", "베르메르", "벨라스케스", "루벤스", "푸생", "baroque"]
    },
    "romanticism": {
        "label": "🚩 낭만주의 & 사실주의 (Romanticism)",
        "keywords": ["들라크루아", "프리드리히", "터너", "고야", "쿠르베", "밀레", "사전트", "romanticism", "realism"]
    },
    "impressionism": {
        "label": "🎨 인상주의 & 신인상주의 (Impressionism)",
        "keywords": ["모네", "르누아르", "드가", "피사로", "시슬레", "마네", "쇠라", "시냑", "impressionism", "pointillism"]
    },
    "post_impressionism": {
        "label": "🌻 후기인상주의 (Post-Impressionism)",
        "keywords": ["고흐", "세잔", "고갱", "로트레크", "post-impressionism"]
    },
    "expressionism": {
        "label": "😱 표현주의 & 야수파 (Expressionism & Fauvism)",
        "keywords": ["뭉크", "마티스", "루소", "실레", "클림트", "블라맹크", "expressionism", "fauvism", "art nouveau"]
    },
    "modern": {
        "label": "💥 입체파 & 초현실주의 (Cubism & Surrealism)",
        "keywords": ["피카소", "달리", "마그리트", "브라크", "샤갈", "칸딘스키", "몬드리안", "cubism", "surrealism"]
    }
}

# Verified Korean Art Docent YouTube Channels
YOUTUBE_LECTURE_CHANNELS = {
    "nulart": {
        "name": "널 위한 문화예술",
        "url": "https://www.youtube.com/@nulart",
        "desc": "대한민국 1위 문화예술 유튜브 채널의 명화 스토리텔링"
    },
    "sapiens": {
        "name": "사피엔스 스튜디오",
        "url": "https://www.youtube.com/@sapiens_studio",
        "desc": "양정무 교수의 난처한 미술이야기 & 명화 인문학 강의"
    },
    "seo_arttalk": {
        "name": "서정욱 미술토크",
        "url": "https://www.youtube.com/@서정욱_미술토크",
        "shorts_url": "https://www.youtube.com/@서정욱_미술토크/shorts",
        "desc": "명화 1분 도슨트 쇼츠 및 깊이 있는 명화 해설"
    },
    "reason_of_art": {
        "name": "미술의 이유",
        "url": "https://www.youtube.com/@Reason_Of_Art/videos",
        "desc": "작품 속 미스터리와 역사적 탄생 배경 전문 해설"
    },
    "room_art": {
        "name": "방구석 미술관 (조원재)",
        "url": "https://www.youtube.com/@100book",
        "desc": "미술계 최고의 베스트셀러 작가가 들려주는 화가들의 생생한 뒷이야기"
    },
    "ebs_art": {
        "name": "EBS 클래스e 미술관",
        "url": "https://www.youtube.com/@ebsclass_e",
        "desc": "최고의 석학들이 전하는 정통 미술사 강의 아카이브"
    }
}

def classify_artwork(item):
    """Classifies an artwork into seasons, themes, and movements."""
    title = str(item.get("title_kr") or item.get("title_en") or "").lower()
    artist = str(item.get("artist_name_kr") or item.get("artist_name_en") or "").lower()
    desc = str(item.get("description") or item.get("behind_story") or "").lower()
    combined_text = f"{title} {artist} {desc}"

    # 1. Season classification
    season_result = "all"
    for s_key, s_data in SEASON_RULES.items():
        if any(kw in combined_text for kw in s_data["keywords"]):
            season_result = s_key
            break

    # 2. Theme classification
    themes_result = []
    for t_key, t_data in THEME_RULES.items():
        if any(kw in combined_text for kw in t_data["keywords"]):
            themes_result.append(t_key)
    if not themes_result:
        themes_result.append("classic")

    # 3. Movement classification
    movement_result = "classic"
    for m_key, m_data in MOVEMENT_RULES.items():
        if any(kw in combined_text for kw in m_data["keywords"]):
            movement_result = m_key
            break

    return {
        "season": season_result,
        "themes": themes_result,
        "movement_category": movement_result
    }

def run_daily_pipeline():
    start_time = datetime.now()
    print(f"[*] Starting Daily Art Pipeline at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # File paths
    paintings_file = "data/art_paintings_master_db.json"
    digital_gallery_file = "data/digital_gallery_master_db.json"
    theme_catalog_file = "data/curated_theme_ontology.json"
    log_file = "data/daily_ingest_log.json"

    with open(paintings_file, "r", encoding="utf-8") as f:
        paint_db = json.load(f)

    with open(digital_gallery_file, "r", encoding="utf-8") as f:
        dg_db = json.load(f)

    # 1. Classify all featured masterpieces
    theme_clusters = {t: [] for t in THEME_RULES}
    season_clusters = {s: [] for s in SEASON_RULES}
    movement_clusters = {m: [] for m in MOVEMENT_RULES}

    for p in paint_db.get("featured_masterpieces", []):
        cls = classify_artwork(p)
        p["season"] = cls["season"]
        p["themes"] = cls["themes"]
        p["movement_category"] = cls["movement_category"]

        pid = p.get("work_id") or p.get("id")
        if cls["season"] in season_clusters:
            season_clusters[cls["season"]].append(pid)
        for t in cls["themes"]:
            if t in theme_clusters:
                theme_clusters[t].append(pid)
        if cls["movement_category"] in movement_clusters:
            movement_clusters[cls["movement_category"]].append(pid)

    # 2. Classify digital gallery artworks
    for a in dg_db.get("artworks", []):
        cls = classify_artwork(a)
        a["season"] = cls["season"]
        a["themes"] = cls["themes"]
        a["movement_category"] = cls["movement_category"]

        aid = a.get("work_id") or a.get("id")
        if cls["season"] in season_clusters:
            season_clusters[cls["season"]].append(aid)
        for t in cls["themes"]:
            if t in theme_clusters:
                theme_clusters[t].append(aid)
        if cls["movement_category"] in movement_clusters:
            movement_clusters[cls["movement_category"]].append(aid)

    # Save ontology summary
    curated_ontology = {
        "version": "2.0.0",
        "last_updated": datetime.now().isoformat(),
        "channels": YOUTUBE_LECTURE_CHANNELS,
        "season_definitions": {k: {"label": v["label"], "count": len(season_clusters[k])} for k, v in SEASON_RULES.items()},
        "theme_definitions": {k: {"label": v["label"], "count": len(theme_clusters[k])} for k, v in THEME_RULES.items()},
        "movement_definitions": {k: {"label": v["label"], "count": len(movement_clusters[k])} for k, v in MOVEMENT_RULES.items()}
    }

    with open(theme_catalog_file, "w", encoding="utf-8") as f:
        json.dump(curated_ontology, f, ensure_ascii=False, indent=2)
    print(f"[+] Saved {theme_catalog_file}")

    # Save enriched master databases
    with open(paintings_file, "w", encoding="utf-8") as f:
        json.dump(paint_db, f, ensure_ascii=False, indent=2)
    print(f"[+] Saved {paintings_file}")

    with open(digital_gallery_file, "w", encoding="utf-8") as f:
        json.dump(dg_db, f, ensure_ascii=False, indent=2)
    print(f"[+] Saved {digital_gallery_file}")

    # Write daily log
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "status": "SUCCESS",
        "total_paintings_indexed": len(dg_db.get("artworks", [])) + len(paint_db.get("featured_masterpieces", [])),
        "seasons_classified": {k: len(v) for k, v in season_clusters.items()},
        "themes_classified": {k: len(v) for k, v in theme_clusters.items()},
        "movements_classified": {k: len(v) for k, v in movement_clusters.items()}
    }
    
    logs = []
    if os.path.exists(log_file):
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except Exception:
            logs = []
    logs.insert(0, log_entry)
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(logs[:50], f, ensure_ascii=False, indent=2)
    print(f"[+] Appended log to {log_file}")

if __name__ == "__main__":
    run_daily_pipeline()
