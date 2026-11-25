import os, json, re

with open('data/digital_gallery_master_db.json', 'r', encoding='utf-8') as f:
    master_db = json.load(f)

artworks = master_db.get('artworks', [])

# Load existing 6 curated themes to preserve their local high-res WebP hero photos
existing_featured = {}
if os.path.exists('data/curated_ambient_themes_db.json'):
    with open('data/curated_ambient_themes_db.json', 'r', encoding='utf-8') as f:
        ex = json.load(f)
        for t in ex.get('curated_themes', []):
            existing_featured[t['id']] = t.get('items', [])

themes_definition = [
    # ── Seasonal Themes (5) ──
    {
        "id": "season_christmas",
        "type": "season",
        "title_kr": "크리스마스 & 윈터 홀리데이",
        "title_en": "Christmas & Winter Holiday",
        "subtitle": "성탄의 설렘과 따스한 불빛, 축복의 성화와 아늑한 겨울 축제",
        "description": "반짝이는 트리와 눈꽃, 따스한 벽난로와 거장들의 성탄 명화가 선사하는 홀리데이의 감동입니다. 온 세상에 울려 퍼지는 평화와 성스러운 온기를 만끽해보세요.",
        "color_accent": "#ef4444",
        "color_tag": "#dc2626",
        "badge": "SEASONAL SPECIAL · CHRISTMAS",
        "default_bgm": "assets/audio/bgm_bach_air.mp3",
        "keywords": ['크리스마스', '성탄', '성모', '아기 예수', '수태고지', '동방박사', '성가족', '천사', 'nativity', 'christmas', 'virgin and child', 'adoration', 'holy family', 'madonna', 'annunciation', 'magi', 'christ', 'angel', 'saint', 'holiday', 'epiphany']
    },
    {
        "id": "season_spring",
        "type": "season",
        "title_kr": "찬란한 봄 & 블라썸",
        "title_en": "Spring & Cherry Blossoms",
        "subtitle": "꽃피는 과수원, 싱그러운 새싹과 따스한 봄 햇살의 왈츠",
        "description": "겨울의 긴 잠을 깨우고 대지를 수놓은 형형색색의 꽃들과 싱그러운 생명력의 향연입니다. 모네와 고흐의 눈부신 봄날 과수원과 정원으로 초대합니다.",
        "color_accent": "#ec4899",
        "color_tag": "#db2777",
        "badge": "SEASONAL · SPRING BLOSSOM",
        "default_bgm": "assets/audio/bgm_clair_de_lune.mp3",
        "keywords": ['봄', '꽃', '벚꽃', '새싹', '과수원', '꽃병', '정원', '튤립', '수련', '장미', 'spring', 'blossom', 'flower', 'orchard', 'rose', 'bouquet', 'bloom', 'flora', 'cherry', 'petal', 'meadow']
    },
    {
        "id": "season_summer",
        "type": "season",
        "title_kr": "청량한 여름 & 오션",
        "title_en": "Summer & Vibrant Ocean",
        "subtitle": "푸른 파도와 에메랄드빛 해변, 눈부신 지중해의 여름 햇살",
        "description": "탁 트인 바다와 청명한 하늘, 파도 소리가 들려오는 시원한 여름 갤러리입니다. 일상의 열기를 시원하게 식혀줄 눈부신 바다와 호수의 파노라마를 만나보세요.",
        "color_accent": "#0284c7",
        "color_tag": "#0369a1",
        "badge": "SEASONAL · SUMMER OCEAN",
        "default_bgm": "assets/audio/bgm_bossa_antigua.mp3",
        "keywords": ['여름', '바다', '해변', '파도', '해수욕', '보트', '지중해', '수영', '태양', 'summer', 'sea', 'ocean', 'beach', 'wave', 'boat', 'marine', 'coast', 'water', 'sail', 'river', 'lake', 'swimming', 'yacht']
    },
    {
        "id": "season_autumn",
        "type": "season",
        "title_kr": "깊어가는 가을 & 낙엽",
        "title_en": "Autumn & Golden Leaves",
        "subtitle": "황금빛 들판과 붉게 물든 단풍, 낭만과 사색의 늦가을 정취",
        "description": "선선한 바람과 함께 온 세상을 금빛과 붉은빛으로 물들이는 가을의 풍요와 고요한 사색의 시간입니다. 낙엽 지는 숲길을 따라 낭만적인 예술의 정취를 거닐어보세요.",
        "color_accent": "#d97706",
        "color_tag": "#b45309",
        "badge": "SEASONAL · AUTUMN GOLD",
        "default_bgm": "assets/audio/bgm_chopin_nocturne.mp3",
        "keywords": ['가을', '낙엽', '단풍', '황금', '추수', '수확', '밀밭', '황혼', '노을', 'autumn', 'fall', 'harvest', 'foliage', 'golden', 'wheat', 'dusk', 'sunset', 'twilight', 'reaper', 'evening']
    },
    {
        "id": "season_winter",
        "type": "season",
        "title_kr": "순백의 겨울 & 설경",
        "title_en": "Winter & Serene Snow",
        "subtitle": "침묵 속에 내려앉은 하얀 눈, 순백의 설산과 얼어붙은 호수의 고요",
        "description": "모든 소음이 멎고 세상이 하얗게 덮인 겨울의 청정하고 신비로운 풍경입니다. 눈 덮인 침엽수림과 알프스의 장엄한 설경을 감상해보세요.",
        "color_accent": "#38bdf8",
        "color_tag": "#0284c7",
        "badge": "SEASONAL · WINTER SNOW",
        "default_bgm": "assets/audio/bgm_gymnopedie.mp3",
        "keywords": ['겨울', '눈', '설경', '설산', '서리', '빙하', '얼음', 'winter', 'snow', 'frost', 'ice', 'glacier', 'blizzard', 'snowy', 'frozen', 'cold']
    },

    # ── Color & Aesthetic Mood Themes (6) ──
    {
        "id": "winter_white",
        "type": "color_mood",
        "title_kr": "겨울에 빛나는 컬러, 화이트",
        "title_en": "Winter White & Pure Snow",
        "subtitle": "순백의 설원과 눈꽃, 하얀 꽃잎과 산토리니의 흰 벽",
        "description": "차가운 겨울에 더욱 빛나며, 언제봐도 마음을 맑고 평온하게 정화시키는 순백의 감성 갤러리입니다. 눈 덮인 들판, 하얀 메모지, 흰 꽃들과 산토리니의 하얀 골목길을 만나보세요.",
        "color_accent": "#f8fafc",
        "color_tag": "#ffffff",
        "badge": "COLOR WHITE · THEME VALLEY",
        "default_bgm": "assets/audio/bgm_gymnopedie.mp3",
        "keywords": ['흰색', '백자', '설경', '백설', '화이트', '하얀', 'white', 'snow', 'porcelain', 'blanc', 'frost', 'marble', 'lily']
    },
    {
        "id": "color_mint",
        "type": "color_mood",
        "title_kr": "싱그러운 청량감, 컬러 민트",
        "title_en": "Fresh Color Mint & Emerald",
        "subtitle": "싱그러운 민트빛 빈티지 카, 청량한 에메랄드빛 해변과 초록의 호흡",
        "description": "일상의 답답함을 시원하게 씻어내고 기분을 상쾌하게 전환시키는 청량한 파스텔 민트의 감성입니다. 에메랄드빛 바다와 싱그러운 잎사귀의 맑은 숨결을 느껴보세요.",
        "color_accent": "#34d399",
        "color_tag": "#10b981",
        "badge": "COLOR MINT · THEME VALLEY",
        "default_bgm": "assets/audio/bgm_bossa_antigua.mp3",
        "keywords": ['초록', '에메랄드', '청록', '비취', '민트', '파스텔', 'green', 'emerald', 'turquoise', 'mint', 'verdant', 'leaves', 'botanical']
    },
    {
        "id": "camping_forest",
        "type": "color_mood",
        "title_kr": "숲과 자연, 힐링 캠핑 & 포레스트",
        "title_en": "Forest Sanctuary & Camping",
        "subtitle": "울창한 침엽수림, 안개 낀 호숫가, 따스한 모닥불과 숲속 텐트",
        "description": "도심의 소음을 벗어나 피톤치드 가득한 깊은 숲에서 누리는 온전한 사색과 휴식의 시간입니다. 타오르는 모닥불과 안개 자욱한 침엽수림 속으로 초대합니다.",
        "color_accent": "#22c55e",
        "color_tag": "#15803d",
        "badge": "HEALING FOREST · THEME VALLEY",
        "default_bgm": "assets/audio/bgm_backbay_lounge.mp3",
        "keywords": ['숲', '나무', '산', '계곡', '자연', '침엽수', '캠핑', '오두막', 'forest', 'woods', 'tree', 'trees', 'mountain', 'landscape', 'nature', 'camp', 'lake']
    },
    {
        "id": "midnight_blue",
        "type": "color_mood",
        "title_kr": "사색의 밤, 미드나잇 블루 & 시티",
        "title_en": "Midnight Blue & City Lights",
        "subtitle": "어두운 밤하늘을 수놓은 은하수, 젖은 도시의 네온 불빛과 고요한 심야",
        "description": "깊어가는 밤, 고요한 음악과 함께 내면의 사색에 몰입하는 시간입니다. 짙푸른 밤하늘의 성운과 비에 젖은 도시의 아스팔트에 반사된 빛무리를 감상해보세요.",
        "color_accent": "#60a5fa",
        "color_tag": "#1e3a8a",
        "badge": "MIDNIGHT NOIR · THEME VALLEY",
        "default_bgm": "assets/audio/bgm_chopin_nocturne.mp3",
        "keywords": ['밤', '별', '달', '야경', '은하수', '심야', '청색', '블루', '심해', 'night', 'star', 'moon', 'nocturne', 'midnight', 'dark', 'evening', 'blue', 'stars']
    },
    {
        "id": "monet_garden",
        "type": "color_mood",
        "title_kr": "빛과 낭만, 모네의 정원과 인상파",
        "title_en": "Monet's Garden & Impressionism",
        "subtitle": "지베르니 정원의 수련, 반짝이는 햇살과 잔잔한 물결의 유화 마티에르",
        "description": "자연의 찰나의 빛과 색채를 캔버스에 영원히 새겨넣은 인상주의 거장들의 낭만적인 야외 테마입니다. 은은하게 흔들리는 지베르니의 수련과 따스한 정원의 오후를 거닐어보세요.",
        "color_accent": "#f59e0b",
        "color_tag": "#d97706",
        "badge": "IMPRESSIONISM · THEME VALLEY",
        "default_bgm": "assets/audio/bgm_clair_de_lune.mp3",
        "keywords": ['모네', '르누아르', '드가', '인상주의', '인상파', '피사로', '시슬레', '세잔', 'monet', 'renoir', 'degas', 'impressionis', 'pissarro', 'sisley', 'cezanne', 'giverny', 'garden', 'water lilies']
    },
    {
        "id": "zen_minimal",
        "type": "color_mood",
        "title_kr": "여백의 미학, 젠 미니멀리즘",
        "title_en": "Zen & Architectural Minimalism",
        "subtitle": "정갈한 돌과 모래, 한 줄기 햇살이 드리운 건축의 비움과 절제",
        "description": "불필요한 장식과 시각적 소음을 덜어내고, 오직 사물의 순수한 형태와 빛과 그림자의 조화에 집중하는 여백의 공간입니다. 마음의 평정과 균형을 찾아보세요.",
        "color_accent": "#94a3b8",
        "color_tag": "#475569",
        "badge": "ZEN MINIMAL · THEME VALLEY",
        "default_bgm": "assets/audio/bgm_bach_air.mp3",
        "keywords": ['정선', '김홍도', '신윤복', '동양화', '수묵', '백자', '달항아리', '이우환', '박서보', '단색화', '여백', '사색', 'zen', 'minimal', 'korean', 'ink', 'monochrome', 'solitude']
    }
]

catalog = {
    "version": "2.0.0",
    "updated_at": "2026-11-26T08:45:00+09:00",
    "total_themes": len(themes_definition),
    "total_classified_artworks": 0,
    "curated_themes": []
}

total_matched_count = 0

for tdef in themes_definition:
    tid = tdef["id"]
    kws = [k.lower() for k in tdef["keywords"]]
    
    # Existing curated featured photos (top 12 hero items)
    feat_items = existing_featured.get(tid, [])
    
    # Classify from 7,865 master artworks
    matched_works = []
    seen_ids = set([x.get('id') for x in feat_items])
    
    for a in artworks:
        text = ' '.join([
            str(a.get('title_kr', '')),
            str(a.get('title_en', '')),
            str(a.get('description', '')),
            str(a.get('curator_notes', '')),
            str(a.get('artist_name_kr', '')),
            str(a.get('artist_name_en', '')),
            str(a.get('movement', '')),
            str(a.get('category_kr', ''))
        ]).lower()
        
        # Check season field directly
        s_val = (a.get('season') or '').lower()
        is_season_match = (
            (tid == 'season_winter' and s_val == 'winter') or
            (tid == 'season_spring' and s_val == 'spring') or
            (tid == 'season_summer' and s_val == 'summer') or
            (tid == 'season_autumn' and s_val == 'autumn')
        )
        
        if is_season_match or any(k in text for k in kws):
            aid = a.get('id') or a.get('work_id')
            if aid in seen_ids:
                continue
            seen_ids.add(aid)
            matched_works.append({
                "id": aid,
                "title": a.get('title_kr') or a.get('title_en') or '무제',
                "artist": a.get('artist_name_kr') or a.get('artist_name_en') or '작가 미상',
                "year": a.get('year') or '',
                "museum": a.get('museum') or '소장처 참조',
                "image_url": a.get('image_url') or a.get('thumbnail_url'),
                "thumbnail_url": a.get('thumbnail_url') or a.get('image_url'),
                "theme_id": tid,
                "color_tag": tdef["color_tag"]
            })
    
    # If this theme doesn't have existing local featured items (e.g. newly added seasonal themes),
    # pick the top 12 best items from matched_works as featured without duplicating
    if not feat_items:
        feat_items = matched_works[:12]
        all_theme_items = matched_works
    else:
        all_theme_items = feat_items + matched_works
    
    theme_entry = {
        "id": tid,
        "type": tdef["type"],
        "title_kr": tdef["title_kr"],
        "title_en": tdef["title_en"],
        "subtitle": tdef["subtitle"],
        "description": tdef["description"],
        "color_accent": tdef["color_accent"],
        "color_tag": tdef["color_tag"],
        "badge": tdef["badge"],
        "default_bgm": tdef["default_bgm"],
        "total_count": len(all_theme_items),
        "hero_image": feat_items[0]["image_url"] if feat_items else "assets/featured/paint_sargent_001.webp",
        "items": all_theme_items # full list for infinite rolling & browsing
    }
    
    catalog["curated_themes"].append(theme_entry)
    total_matched_count += len(all_theme_items)
    print(f"[{tdef['type'].upper()}] {tdef['title_kr']}: {len(all_theme_items):,} items indexed")

catalog["total_classified_artworks"] = total_matched_count

with open('data/curated_ambient_themes_db.json', 'w', encoding='utf-8') as f:
    json.dump(catalog, f, ensure_ascii=False, indent=2)

print(f"\nSuccessfully generated data/curated_ambient_themes_db.json! Total theme artworks indexed: {total_matched_count:,}")
