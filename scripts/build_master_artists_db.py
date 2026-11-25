import json, re

CHOSUNG_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

def get_chosung(char):
    if '가' <= char <= '힣':
        code = ord(char) - 0xAC00
        chosung_index = code // (21 * 28)
        ch = CHOSUNG_LIST[chosung_index]
        # Normalize double consonants to base
        norm_map = {'ㄲ': 'ㄱ', 'ㄸ': 'ㄷ', 'ㅃ': 'ㅂ', 'ㅆ': 'ㅅ', 'ㅉ': 'ㅈ'}
        return norm_map.get(ch, ch)
    return None

def get_alpha_group(name_en, name_kr):
    # Determine Korean initial
    kr_char = name_kr.strip()[0] if name_kr and name_kr.strip() else ''
    cho = get_chosung(kr_char)
    
    # Determine English initial
    en_clean = re.sub(r'[^A-Za-z]', '', name_en or '').upper()
    en_init = en_clean[0] if en_clean else 'ETC'
    
    return cho or '기타', en_init

# Collect all artworks
db_files = [
    'data/art_paintings_master_db.json',
    'data/expanded_art_categories_db.json',
    'data/contemporary_art_and_architecture_db.json',
    'data/digital_gallery_master_db.json'
]

raw_artworks = []
for p in db_files:
    try:
        with open(p, 'r', encoding='utf-8') as f:
            d = json.load(f)
        if isinstance(d, dict):
            for k, v in d.items():
                if isinstance(v, list): raw_artworks.extend(v)
                elif isinstance(v, dict):
                    for subk, subv in v.items():
                        if isinstance(subv, list): raw_artworks.extend(subv)
    except Exception as e:
        print(f"Error reading {p}: {e}")

# Aggregate by artist
artist_map = {}
chinese_name_map = {
    '金弘道': ('김홍도', 'Kim Hong-do', '조선 3대 풍속화 거장', '조선 (Joseon)', '1745 ~ 1806경', '조선 풍속화·진경산수'),
    '鄭歚': ('겸재 정선', 'Jeong Seon', '진경산수화의 개조', '조선 (Joseon)', '1676 ~ 1759', '진경산수화'),
    '姜世晃': ('강세황', 'Kang Se-hwang', '시서화 삼절의 예원 총수', '조선 (Joseon)', '1713 ~ 1791', '남종문인화'),
    '申潤福': ('혜원 신윤복', 'Shin Yun-bok', '조선 서민과 여인의 삶을 빚은 풍속화 거장', '조선 (Joseon)', '1758 ~ 1813경', '조선 풍속화'),
    '張承業': ('오원 장승업', 'Jang Seung-eop', '조선 말기 천재 화원', '조선 (Joseon)', '1843 ~ 1897', '조선 말기 회화')
}

for art in raw_artworks:
    if not isinstance(art, dict): continue
    name_kr = (art.get('artist_name_kr') or art.get('artist') or '').strip()
    name_en = (art.get('artist_name_en') or '').strip()
    
    if not name_kr or len(name_kr) < 2: continue
    
    # Handle Chinese character names
    if name_kr in chinese_name_map:
        mapped = chinese_name_map[name_kr]
        name_kr = mapped[0]
        if not name_en: name_en = mapped[1]

    # Clean brackets or parentheses
    clean_kr = re.sub(r'\(.*?\)', '', name_kr).strip()
    key = clean_kr.lower()

    if key not in artist_map:
        artist_map[key] = {
            "name_kr": clean_kr,
            "name_en": name_en,
            "artworks": [],
            "sample_images": [],
            "movements": set(),
            "museums": set(),
            "years": set(),
            "materials": set()
        }
    
    a_rec = artist_map[key]
    if name_en and not a_rec["name_en"]:
        a_rec["name_en"] = name_en
    
    art_id = art.get('id') or art.get('work_id')
    thumb = art.get('thumbnail_url') or art.get('image_url')
    if thumb and len(a_rec["sample_images"]) < 4:
        a_rec["sample_images"].append(thumb)
    
    a_rec["artworks"].append(art_id)
    if art.get('genre'): a_rec["movements"].add(art.get('genre'))
    if art.get('movement'): a_rec["movements"].add(art.get('movement'))
    if art.get('museum'): a_rec["museums"].add(art.get('museum'))
    if art.get('year'): a_rec["years"].add(str(art.get('year')))
    if art.get('medium'): a_rec["materials"].add(art.get('medium'))

print(f"Aggregated {len(artist_map)} unique artists from masterpieces database.")

# Master Dossier enrichments from people db
try:
    with open('data/lets_people_artists.json', 'r', encoding='utf-8') as f:
        people_dossiers = json.load(f).get('featured_masters', [])
except:
    people_dossiers = []

dossier_by_name = {}
for p in people_dossiers:
    if p.get('name_kr'): dossier_by_name[p['name_kr'].lower()] = p
    if p.get('name_en'): dossier_by_name[p['name_en'].lower()] = p

# Build comprehensive artist array
final_artists = []
for k, v in artist_map.items():
    name_kr = v["name_kr"]
    name_en = v["name_en"]
    
    # Check dossier match
    matched_dos = None
    for dk, dos in dossier_by_name.items():
        if dk in name_kr.lower() or name_kr.lower() in dk:
            matched_dos = dos
            break
        if name_en and (dk in name_en.lower() or name_en.lower() in dk):
            matched_dos = dos
            break

    # Categorize Chosung and Alpha
    cho, alpha = get_alpha_group(name_en, name_kr)
    
    # Clean avatar image
    avatar = ""
    if matched_dos and matched_dos.get('profile_image'):
        avatar = matched_dos['profile_image']
    elif v["sample_images"]:
        avatar = v["sample_images"][0]
    else:
        avatar = "assets/icons/favicon-32.png"

    # Description
    desc = ""
    if matched_dos and matched_dos.get('summary'):
        desc = matched_dos['summary']
    else:
        movements_str = ", ".join(list(v["movements"])[:2]) if v["movements"] else "서양 고전·근현대 회화"
        desc = f"{name_kr}({name_en or 'Artist'})의 주요 예술 세계. {movements_str} 분야에서 탁월한 조형적 성취를 남긴 거장."

    lifespan = matched_dos.get('lifespan') if matched_dos else ""
    if not lifespan and v["years"]:
        sorted_years = sorted([int(y) for y in v["years"] if y.isdigit()])
        if sorted_years:
            lifespan = f"활동기 {sorted_years[0]}년 ~ {sorted_years[-1]}년"

    nationality = matched_dos.get('nationality') if matched_dos else ""
    movement = matched_dos.get('movement') if matched_dos else (list(v["movements"])[0] if v["movements"] else "세계 미술사")

    final_artists.append({
        "id": "art_" + re.sub(r'[^a-zA-Z0-9_]', '_', (name_en or name_kr).lower())[:24],
        "name_kr": name_kr,
        "name_en": name_en,
        "chosung": cho,
        "alpha": alpha,
        "lifespan": lifespan or "시대 미상",
        "nationality": nationality or "글로벌 문화유산",
        "movement": movement,
        "description": desc,
        "avatar": avatar,
        "work_count": len(v["artworks"]),
        "artwork_ids": v["artworks"][:40],
        "museums": list(v["museums"])[:3]
    })

# Sort by artwork count descending
final_artists.sort(key=lambda x: -x["work_count"])

output_data = {
    "version": "4.0.0",
    "total_artists": len(final_artists),
    "chosung_indices": CHOSUNG_LIST,
    "alpha_indices": [chr(i) for i in range(ord('A'), ord('Z')+1)],
    "artists": final_artists
}

with open('data/master_artists_directory.json', 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f"Successfully generated data/master_artists_directory.json with {len(final_artists)} artists.")
