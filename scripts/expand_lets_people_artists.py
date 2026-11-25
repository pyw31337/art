#!/usr/bin/env python3
import json

with open('data/lets_people_artists.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

masters = data.get('featured_masters', [])
existing_ids = {m['id'] for m in masters}

new_artists = [
    {
        "id": "artist_auguste_rodin",
        "urn": "urn:people:person:historical:auguste_rodin",
        "art_urn": "urn:art:artist:auguste_rodin",
        "name_kr": "오귀스트 로댕",
        "name_en": "Auguste Rodin",
        "name_orig": "François-Auguste-René Rodin",
        "lifespan": "1840 ~ 1917 (향년 77세)",
        "nationality": "프랑스 (파리)",
        "movement": "근대 조각 (Modern Sculpture)",
        "category": "fine_art_masters",
        "profile_image": "https://pub-685f237e5a544431bee558c5b29f3291.r2.dev/featured/thumbs/sculpt_rodin_thinker.webp",
        "summary": "전통적인 아카데미즘과 이상주의적 미학을 탈피하여, 거친 표면과 근육의 팽팽한 긴장감 속에 인간의 실존적 고뇌와 생명력을 빚어낸 '근대 조각의 아버지'.",
        "artistic_lineage": {
            "influenced_by": ["미켈란젤로 부오나로티", "단테 알리기에리"],
            "contemporaries_and_allies": ["카미유 클로델", "앙리 마티스", "라이너 마리아 릴케 (비서 겸 전기 작가)"],
            "influenced": ["콘스탄틴 브랑쿠시", "알베르토 자코메티"]
        },
        "famous_quote": "조각은 군더더기를 깎아내고 남은 생명의 본질이다."
    },
    {
        "id": "artist_john_singer_sargent",
        "urn": "urn:people:person:historical:john_singer_sargent",
        "art_urn": "urn:art:artist:john_singer_sargent",
        "name_kr": "존 싱어 사전트",
        "name_en": "John Singer Sargent",
        "name_orig": "John Singer Sargent",
        "lifespan": "1856 ~ 1925 (향년 69세)",
        "nationality": "미국 / 프랑스 / 영국",
        "movement": "사실주의 및 인상주의 초상화",
        "category": "fine_art_masters",
        "profile_image": "https://pub-685f237e5a544431bee558c5b29f3291.r2.dev/featured/thumbs/paint_sargent_001.webp",
        "summary": "벨 에포크 시대 상류사회의 심리적 기류와 우아함을 번개 같은 붓질로 포착한 세기의 초상화 거장. 살롱전을 뒤흔든 <마담 X>로 미술사의 전환점을 만듦.",
        "artistic_lineage": {
            "mentor": "카롤뤼스 뒤랑 (Carolus-Duran)",
            "allies": ["클로드 모네", "헨리 제임스"],
            "influenced": ["20세기 모던 패션 및 인물화"]
        },
        "famous_quote": "초상은 입에 무언가 살짝 잘못된 것이 있는 그림이다."
    },
    {
        "id": "artist_hendrik_van_anthonissen",
        "urn": "urn:people:person:historical:hendrik_van_anthonissen",
        "art_urn": "urn:art:artist:hendrik_van_anthonissen",
        "name_kr": "헨드릭 판 안토니선",
        "name_en": "Hendrik van Anthonissen",
        "name_orig": "Hendrik van Anthonissen",
        "lifespan": "1605 ~ 1656 (향년 51세)",
        "nationality": "네덜란드 (헤이그/암스테르담)",
        "movement": "네덜란드 황금시대 해양화 (Dutch Golden Age Marine)",
        "category": "fine_art_masters",
        "profile_image": "https://pub-685f237e5a544431bee558c5b29f3291.r2.dev/featured/thumbs/paint_anthonissen_whale.webp",
        "summary": "17세기 네덜란드 바다의 대기와 포말, 해변의 일상을 사실적으로 묘사한 해양화가. 케임브리지 피츠윌리엄 박물관의 복원 과정을 통해 140년 만에 숨겨진 고래가 발견되어 세계적 조명을 받음.",
        "artistic_lineage": {
            "mentor": "아르놀투스 판 안토니선 (아버지)",
            "allies": ["얀 포르셀리스 (처남이자 스승)"],
            "influenced": ["17세기 북유럽 해양 풍경화파"]
        },
        "famous_quote": "바다는 인간의 모든 침묵과 거친 진실을 동시에 품는다."
    },
    {
        "id": "artist_pablo_picasso",
        "urn": "urn:people:person:historical:pablo_picasso",
        "art_urn": "urn:art:artist:pablo_picasso",
        "name_kr": "파블로 피카소",
        "name_en": "Pablo Picasso",
        "name_orig": "Pablo Ruiz y Picasso",
        "lifespan": "1881 ~ 1973 (향년 91세)",
        "nationality": "스페인 / 프랑스",
        "movement": "입체주의 (Cubism) 창시자",
        "category": "fine_art_masters",
        "profile_image": "https://pub-685f237e5a544431bee558c5b29f3291.r2.dev/featured/thumbs/art_picasso_demoiselles.webp",
        "summary": "단일 시점의 원근법을 깨뜨리고 다각도의 다시점(Multi-perspective)을 한 화면에 중첩한 입체파의 혁명가이자 20세기 현대 미술의 절대적 거장.",
        "artistic_lineage": {
            "allies": ["조르주 브라크 (입체파 공동 창시)", "앙리 마티스 (평생의 라이벌)"],
            "influenced": ["미래주의", "초현실주의", "구성주의", "추상표현주의"]
        },
        "famous_quote": "모든 어린이는 예술가다. 문제는 어떻게 어른이 되어서도 예술가로 남느냐는 것이다."
    },
    {
        "id": "artist_alberto_giacometti",
        "urn": "urn:people:person:historical:alberto_giacometti",
        "art_urn": "urn:art:artist:alberto_giacometti",
        "name_kr": "알베르토 자코메티",
        "name_en": "Alberto Giacometti",
        "name_orig": "Alberto Giacometti",
        "lifespan": "1901 ~ 1966 (향년 65세)",
        "nationality": "스위스 / 프랑스",
        "movement": "실존주의 조각 (Existentialist Art)",
        "category": "fine_art_masters",
        "profile_image": "https://pub-685f237e5a544431bee558c5b29f3291.r2.dev/featured/thumbs/sculpt_giacometti_walking_man.webp",
        "summary": "2차 세계대전의 참상 이후 군더더기 살점을 모두 깎아내고 뼈대만 앙상하게 남은 가느다란 청동 조각으로 인간의 근원적 고독과 존엄성을 조각한 실존주의 예술의 거장.",
        "artistic_lineage": {
            "allies": ["장 폴 사르트르 (실존주의 철학적 동반자)", "시몬 드 보부아르"],
            "influenced": ["현대 개념미술 및 미니멀리즘 조각"]
        },
        "famous_quote": "나는 조각을 만드는 것이 아니라, 텅 빈 공간 속의 인간의 시선을 빚는다."
    },
    {
        "id": "artist_jeong_seon",
        "urn": "urn:people:person:historical:jeong_seon",
        "art_urn": "urn:art:artist:jeong_seon",
        "name_kr": "겸재 정선",
        "name_en": "Jeong Seon",
        "name_orig": "鄭敾",
        "lifespan": "1676 ~ 1759 (향년 83세)",
        "nationality": "조선 (Joseon Korea)",
        "movement": "진경산수화 (眞景山水畫)",
        "category": "fine_art_masters",
        "profile_image": "https://pub-685f237e5a544431bee558c5b29f3291.r2.dev/featured/thumbs/asian_jeongseon_inwang.webp",
        "summary": "중국 산수를 모방하던 관념적 화풍을 과감히 혁파하고, 조선의 산천을 직접 발로 디디며 장쾌한 필치와 독창적인 부벽준법으로 조선 회화의 르네상스를 연 대화성.",
        "artistic_lineage": {
            "allies": ["사천 이병연 (평생의 시우)", "영조 (왕실의 각별한 신임)"],
            "influenced": ["단원 김홍도", "이인상", "조선 후기 화단 전체"]
        },
        "famous_quote": "우리 산천의 기운을 그대로 옮겨 붓끝에 조선의 뼈대를 세운다."
    }
]

for artist in new_artists:
    if artist['id'] not in existing_ids:
        masters.append(artist)
        existing_ids.add(artist['id'])

data['featured_masters'] = masters
data['total_masters_indexed'] = len(masters)

with open('data/lets_people_artists.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Total Let's People artists dossier updated to {len(masters)} masters.")
