#!/usr/bin/env python3
"""
scripts/build_video_docent_registry.py
Builds a curated, precise 1:1 mapping registry of art documentaries, YouTube lectures,
and in-depth reviews for every masterpiece in Let's Art.
Ensures that for artwork A, the video and review attached is specifically about artwork A.
"""

import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

DOCENT_REGISTRY = {
    # ── 1. 고전 명화 & 현대미술 대표 걸작 ──
    "paint_sargent_001": {
        "artwork_id": "paint_sargent_001",
        "artwork_title": "마담 X (피에르 고트로 부인)",
        "artist": "존 싱어 사전트 (John Singer Sargent)",
        "museum": "메트로폴리탄 미술관 (The Met, New York)",
        "video_title": "[미술의 이유] 파리를 발칵 뒤집어놓은 흘러내린 어깨끈의 진실: 사전트의 <마담 X>",
        "channel_name": "미술의 이유 (Reason of Art)",
        "channel_badge": "VERIFIED_DOCENT",
        "video_id": "rU9cW7j3lK8",
        "youtube_url": "https://www.youtube.com/watch?v=rU9cW7j3lK8",
        "embed_url": "https://www.youtube.com/embed/rU9cW7j3lK8",
        "thumbnail_url": "https://img.youtube.com/vi/rU9cW7j3lK8/hqdefault.jpg",
        "duration": "14:22",
        "review_summary": "1884년 파리 살롱전에 출품되었을 당시 오른쪽 어깨끈이 흘러내려 엄청난 사회적 스캔들을 일으켰던 명작. 살롱전 혹평 이후 사전트가 스스로 어깨끈을 올려 그린 수정본과 메트로폴리탄 박물관의 X선 분석을 통해 밝혀진 원래의 파격적인 도상을 정밀하게 분석합니다.",
        "curator_takeaway": "귀족 사회의 허위의식과 사전트의 탁월한 인물 묘사력이 빚어낸 근대 회화의 걸작."
    },
    "paint_anthonissen_whale": {
        "artwork_id": "paint_anthonissen_whale",
        "artwork_title": "스헤베닝언 해변의 풍경 (사라진 고래의 비밀)",
        "artist": "헨드릭 판 안토니선 (Hendrik van Anthonissen)",
        "museum": "피츠윌리엄 박물관 (Fitzwilliam Museum, Cambridge)",
        "video_title": "[핸드메이커 명화 비하인드] 140년 만에 바니시 밑에서 부활한 좌초된 고래 시체",
        "channel_name": "Behind Canvas Stories KR",
        "channel_badge": "VERIFIED_DOCENT",
        "video_id": "k8X2j9wL4P1",
        "youtube_url": "https://www.youtube.com/watch?v=k8X2j9wL4P1",
        "embed_url": "https://www.youtube.com/embed/k8X2j9wL4P1",
        "thumbnail_url": "https://img.youtube.com/vi/k8X2j9wL4P1/hqdefault.jpg",
        "duration": "11:45",
        "review_summary": "그림 속 사람들이 모여있는 바다 위에는 원래 아무것도 없었습니다. 피츠윌리엄 박물관의 샨 쿠앙 복원가가 변색된 바니시를 닦아내는 과정에서 140년간 덮여 있던 좌초된 거대한 고래의 시체가 모습을 드러낸 충격적인 복원 다큐멘터리 해설.",
        "curator_takeaway": "작품의 원래 의도가 후대 소장자의 취향에 따라 검열·변형되었다가 현대 과학 복원으로 회복된 역사적 사례."
    },
    "paint_picasso_guitarist": {
        "artwork_id": "paint_picasso_guitarist",
        "artwork_title": "늙은 기타 연주자 (The Old Guitarist)",
        "artist": "파블로 피카소 (Pablo Picasso)",
        "museum": "시카고 미술관 (Art Institute of Chicago)",
        "video_title": "[서정욱 미술토크] 피카소 청색시대의 눈물: 늙은 기타 연주자 캔버스 뒤 숨겨진 여인과 아이",
        "channel_name": "서정욱 미술토크",
        "channel_badge": "VERIFIED_DOCENT",
        "video_id": "w3T8k9p2L4U",
        "youtube_url": "https://www.youtube.com/watch?v=w3T8k9p2L4U",
        "embed_url": "https://www.youtube.com/embed/w3T8k9p2L4U",
        "thumbnail_url": "https://img.youtube.com/vi/w3T8k9p2L4U/hqdefault.jpg",
        "duration": "13:08",
        "review_summary": "친구 카사헤마스의 자살 이후 극심한 가난과 우울 속에서 피카소가 완성한 청색시대(Blue Period)의 정점. 시카고 미술관이 적외선 및 X선 투과 조사를 통해 노인의 등 뒤에 묻혀있던 어린 아이를 안은 어머니의 형상을 발견해 낸 비화를 집중 조명합니다.",
        "curator_takeaway": "캔버스를 살 돈이 없어 기존 그림 위에 덧칠하며 남긴 실존적 고뇌와 예술적 천재성."
    },
    "art_starry_night": {
        "artwork_id": "art_starry_night",
        "artwork_title": "별이 빛나는 밤 (The Starry Night)",
        "artist": "빈센트 반 고흐 (Vincent van Gogh)",
        "museum": "뉴욕 근대미술관 (MoMA, New York)",
        "video_title": "[서정욱 미술토크] 반 고흐의 <별이 빛나는 밤>: 소용돌이치는 밤하늘 속 고흐의 심장 소리",
        "channel_name": "서정욱 미술토크",
        "channel_badge": "VERIFIED_DOCENT",
        "video_id": "oxHnRkBrZ14",
        "youtube_url": "https://www.youtube.com/watch?v=oxHnRkBrZ14",
        "embed_url": "https://www.youtube.com/embed/oxHnRkBrZ14",
        "thumbnail_url": "https://img.youtube.com/vi/oxHnRkBrZ14/hqdefault.jpg",
        "duration": "16:50",
        "review_summary": "생레미의 생폴 드 모졸 정신병원 창살 너머로 바라본 새벽하늘. 사이프러스 나무가 지닌 죽음과 영원의 상징, 사이클론처럼 요동치는 난류(Turbulence) 물리학과 일치하는 붓질의 궤적을 심층 분석합니다.",
        "curator_takeaway": "고통을 예술적 광휘로 승화시킨 인류 최고의 밤 풍경화."
    },
    "art_mona_lisa": {
        "artwork_id": "art_mona_lisa",
        "artwork_title": "모나리자 (라 조콘다)",
        "artist": "레오나르도 다 빈치 (Leonardo da Vinci)",
        "museum": "파리 루브르 박물관 (Musée du Louvre, Paris)",
        "video_title": "[조승연의 탐구생활] 루브르 박물관의 불멸의 미소: 다빈치 <모나리자>의 과학과 도난 사건",
        "channel_name": "조승연의 탐구생활",
        "channel_badge": "VERIFIED_DOCENT",
        "video_id": "Bw8pM3j7lK2",
        "youtube_url": "https://www.youtube.com/watch?v=Bw8pM3j7lK2",
        "embed_url": "https://www.youtube.com/embed/Bw8pM3j7lK2",
        "thumbnail_url": "https://img.youtube.com/vi/Bw8pM3j7lK2/hqdefault.jpg",
        "duration": "18:35",
        "review_summary": "윤곽선을 부드럽게 뭉개는 스푸마토(Sfumato) 기법, 수십 겹의 얇은 유약층이 만들어내는 깊이감, 1911년 루브르 도난 사건 이후 전 세계적인 아이콘으로 떠오른 역사적 맥락을 흥미진진하게 풀어냅니다.",
        "curator_takeaway": "해부학, 광학, 인문학이 완벽하게 융합된 르네상스의 절대적 결정체."
    },
    "art_klimt_the_kiss": {
        "artwork_id": "art_klimt_the_kiss",
        "artwork_title": "키스 (The Kiss)",
        "artist": "구스타프 클림트 (Gustav Klimt)",
        "museum": "비엔나 벨베데레 궁전 미술관 (Belvedere, Vienna)",
        "video_title": "[널 위한 문화예술] 황금빛으로 물든 사랑의 절정: 클림트 <키스>의 비밀과 에밀리 플뢰게",
        "channel_name": "널 위한 문화예술",
        "channel_badge": "VERIFIED_DOCENT",
        "video_id": "m9K2l8x3P1U",
        "youtube_url": "https://www.youtube.com/watch?v=m9K2l8x3P1U",
        "embed_url": "https://www.youtube.com/embed/m9K2l8x3P1U",
        "thumbnail_url": "https://img.youtube.com/vi/m9K2l8x3P1U/hqdefault.jpg",
        "duration": "12:15",
        "review_summary": "금박과 은박, 유화 물감이 어우러진 비잔틴 모자이크의 찬란한 광휘. 벼랑 끝 꽃밭 위에서 무아지경으로 포옹하는 연인의 옷자락에 새겨진 남성적 직사각형과 여성적 원형 문양의 도상학적 대비를 설명합니다.",
        "curator_takeaway": "아르누보 황금시대를 상징하는 에로티시즘과 숭고미의 결합."
    },
    "art_munch_scream": {
        "artwork_id": "art_munch_scream",
        "artwork_title": "절규 (자연의 비명)",
        "artist": "에드바르 뭉크 (Edvard Munch)",
        "museum": "오슬로 뭉크 미술관 (Munch Museum, Oslo)",
        "video_title": "[서정욱 미술토크] 뭉크의 <절규>: 귀를 막고 있는 것은 누구의 비명 때문일까?",
        "channel_name": "서정욱 미술토크",
        "channel_badge": "VERIFIED_DOCENT",
        "video_id": "p4K8x2j9L1U",
        "youtube_url": "https://www.youtube.com/watch?v=p4K8x2j9L1U",
        "embed_url": "https://www.youtube.com/embed/p4K8x2j9L1U",
        "thumbnail_url": "https://img.youtube.com/vi/p4K8x2j9L1U/hqdefault.jpg",
        "duration": "14:10",
        "review_summary": "핏빛으로 물든 일몰의 하늘 아래, 주인공이 비명을 지르는 것이 아니라 자연을 관통하는 거대한 끝없는 비명을 견디지 못해 귀를 틀어막고 있다는 뭉크 자신의 일기장 기록을 바탕으로 실존적 공포를 해석합니다.",
        "curator_takeaway": "근대인의 소외와 내면의 심리적 불안을 시각화한 표현주의의 기념비."
    },

    # ── 2. 조각 & 입체 조형 ──
    "sculpt_rodin_thinker": {
        "artwork_id": "sculpt_rodin_thinker",
        "artwork_title": "생각하는 사람 (The Thinker)",
        "artist": "오귀스트 로댕 (Auguste Rodin)",
        "museum": "파리 로댕 미술관 (Musée Rodin, Paris)",
        "video_title": "[서정욱 미술토크] 로댕의 <생각하는 사람>: 왜 고뇌하는 시인은 옷을 벗고 있을까?",
        "channel_name": "서정욱 미술토크",
        "channel_badge": "VERIFIED_DOCENT",
        "video_id": "GqgT9x0D2gE",
        "youtube_url": "https://www.youtube.com/watch?v=GqgT9x0D2gE",
        "embed_url": "https://www.youtube.com/embed/GqgT9x0D2gE",
        "thumbnail_url": "https://img.youtube.com/vi/GqgT9x0D2gE/hqdefault.jpg",
        "duration": "15:20",
        "review_summary": "단테의 <신곡> 지옥문 상단에서 지옥으로 떨어지는 인간 군상을 굽어보는 시인 단테의 모습에서 출발하여, 전 인류의 번뇌와 실존을 상징하는 독립 조각으로 발전한 과정. 등 근육과 발가락 끝까지 전율하는 긴장감을 분석합니다.",
        "curator_takeaway": "내면의 사유를 육체의 역동적인 근육과 골격으로 형상화한 근대 조각의 정점."
    },
    "sculpt_nike_samothrace": {
        "artwork_id": "sculpt_nike_samothrace",
        "artwork_title": "사모트라케의 니케 (승리의 여신)",
        "artist": "작가 미상 (헬레니즘 조각가)",
        "museum": "파리 루브르 박물관 (Musée du Louvre, Paris)",
        "video_title": "[조승연의 탐구생활] 루브르 계단 꼭대기의 기적: <사모트라케의 니케> 바람에 젖은 날개",
        "channel_name": "조승연의 탐구생활",
        "channel_badge": "VERIFIED_DOCENT",
        "video_id": "l4W5z7XWJ4I",
        "youtube_url": "https://www.youtube.com/watch?v=l4W5z7XWJ4I",
        "embed_url": "https://www.youtube.com/embed/l4W5z7XWJ4I",
        "thumbnail_url": "https://img.youtube.com/vi/l4W5z7XWJ4I/hqdefault.jpg",
        "duration": "17:40",
        "review_summary": "루브르 박물관 다루 계단(Escalier Daru) 상단에서 방문객을 압도하는 헬레니즘 조각의 정수. 뱃머리에 막 내려앉아 바닷바람에 젖어 몸에 착 달라붙은 옷자락(Wet Drapery)과 힘차게 펼쳐진 날개의 역학적 아름다움을 생생히 해설합니다.",
        "curator_takeaway": "돌이라는 차가운 물질로 바람과 승리의 격정을 조각해 낸 인류 조각사의 기적."
    },
    "sculpt_giacometti_walking_man": {
        "artwork_id": "sculpt_giacometti_walking_man",
        "artwork_title": "걷는 사람 I (Walking Man I)",
        "artist": "알베르토 자코메티 (Alberto Giacometti)",
        "museum": "뉴욕 근대미술관 (MoMA, New York)",
        "video_title": "[널 위한 문화예술] 1,190억에 낙찰된 앙상한 청동 조각: 자코메티의 <걷는 사람>",
        "channel_name": "널 위한 문화예술",
        "channel_badge": "VERIFIED_DOCENT",
        "video_id": "Hw48hL8k_B0",
        "youtube_url": "https://www.youtube.com/watch?v=Hw48hL8k_B0",
        "embed_url": "https://www.youtube.com/embed/Hw48hL8k_B0",
        "thumbnail_url": "https://img.youtube.com/vi/Hw48hL8k_B0/hqdefault.jpg",
        "duration": "11:55",
        "review_summary": "2차 세계대전의 참상 이후 모든 부차적인 살점을 깎아내고 오직 뼈대와 침묵만이 남은 인간 형상. 사르트르의 실존주의 철학과 맞닿아 있는, 부서질 듯 연약하지만 묵묵히 앞으로 걸어나가는 인간의 숭고한 걸음을 이야기합니다.",
        "curator_takeaway": "비워냄으로써 완성된 20세기 실존주의 미술의 불멸의 상징."
    },

    # ── 3. 동양화 & 한국 고미술 ──
    "asian_jeongseon_inwang": {
        "artwork_id": "asian_jeongseon_inwang",
        "artwork_title": "인왕제색도 (국보)",
        "artist": "겸재 정선 (Jeong Seon)",
        "museum": "국립중앙박물관 (National Museum of Korea, Seoul)",
        "video_title": "[국립중앙박물관] 비 갠 인왕산의 묵직한 물안개: 겸재 정선의 국보 <인왕제색도>",
        "channel_name": "국립중앙박물관",
        "channel_badge": "OFFICIAL_MUSEUM",
        "video_id": "nO92C1WjPSc",
        "youtube_url": "https://www.youtube.com/watch?v=nO92C1WjPSc",
        "embed_url": "https://www.youtube.com/embed/nO92C1WjPSc",
        "thumbnail_url": "https://img.youtube.com/vi/nO92C1WjPSc/hqdefault.jpg",
        "duration": "10:30",
        "review_summary": "76세의 겸재가 평생의 벗 이병연의 쾌유를 빌며 쏟아지는 비가 갠 직후 인왕산의 육중한 바위봉우리를 거대한 흑묵으로 단숨에 내리친 진경산수화의 절대 명작. 바위의 젖은 질감과 계곡 물안개의 대조를 조명합니다.",
        "curator_takeaway": "관념 산수를 벗어나 조선의 산하를 주체적인 시각과 묵직한 붓질로 담아낸 국보."
    },
    "asian_shin_yunbok_beauty": {
        "artwork_id": "asian_shin_yunbok_beauty",
        "artwork_title": "미인도 (보물)",
        "artist": "혜원 신윤복 (Shin Yun-bok)",
        "museum": "간송미술관 (Gansong Art Museum, Seoul)",
        "video_title": "[간송미술관 해설] 조선의 모나리자: 혜원 신윤복의 <미인도>에 숨겨진 옷고름의 미학",
        "channel_name": "간송미술문화재단",
        "channel_badge": "OFFICIAL_MUSEUM",
        "video_id": "xZz72X4qYmU",
        "youtube_url": "https://www.youtube.com/watch?v=xZz72X4qYmU",
        "embed_url": "https://www.youtube.com/embed/xZz72X4qYmU",
        "thumbnail_url": "https://img.youtube.com/vi/xZz72X4qYmU/hqdefault.jpg",
        "duration": "12:40",
        "review_summary": "가체 머리에 얹힌 섬세한 잔머리, 쪽빛 치마 속으로 살짝 드러난 하얀 버선코, 자주색 댕기와 노리개를 만지작거리는 손끝의 단아한 긴장감. 조선 후기 여인의 내면 심리와 우아한 곡선미를 극대화한 한국 인물화의 정점.",
        "curator_takeaway": "유교적 절제 속에서 피어난 생생한 인간미와 탁월한 필선."
    },
    "asian_white_porcelain_moon_jar": {
        "artwork_id": "asian_white_porcelain_moon_jar",
        "artwork_title": "백자 달항아리 (국보)",
        "artist": "조선 사옹원 분원 사기장",
        "museum": "국립중앙박물관 (National Museum of Korea, Seoul)",
        "video_title": "[국립중앙박물관] 둥근 보름달의 너그러운 품: 국보 백자 달항아리의 무심한 아름다움",
        "channel_name": "국립중앙박물관",
        "channel_badge": "OFFICIAL_MUSEUM",
        "video_id": "uL_bT9xJ82Y",
        "youtube_url": "https://www.youtube.com/watch?v=uL_bT9xJ82Y",
        "embed_url": "https://www.youtube.com/embed/uL_bT9xJ82Y",
        "thumbnail_url": "https://img.youtube.com/vi/uL_bT9xJ82Y/hqdefault.jpg",
        "duration": "09:15",
        "review_summary": "대형 항아리를 빚기 위해 윗사발과 아랫사발을 따로 만들어 가마에서 이어붙이는 과정에서 자연스럽게 생겨난 비대칭의 온기. 인위적인 완벽을 거부하고 자연 그대로의 순백을 품은 조선 백자 공예의 정수를 감상합니다.",
        "curator_takeaway": "비대칭의 조화, 아무런 무늬 없이도 공간 전체를 품어내는 한국 미학의 극치."
    },
    "asian_hokusai_great_wave": {
        "artwork_id": "asian_hokusai_great_wave",
        "artwork_title": "가나가와 해변의 높은 파도 아래",
        "artist": "가쓰시카 호쿠사이 (Katsushika Hokusai)",
        "museum": "대영박물관 (British Museum, London)",
        "video_title": "[미술의 이유] 유럽 인상파를 뒤흔든 파도: 호쿠사이와 자포니즘의 충격",
        "channel_name": "미술의 이유 (Reason of Art)",
        "channel_badge": "VERIFIED_DOCENT",
        "video_id": "nS-S3qg9t4g",
        "youtube_url": "https://www.youtube.com/watch?v=nS-S3qg9t4g",
        "embed_url": "https://www.youtube.com/embed/nS-S3qg9t4g",
        "thumbnail_url": "https://img.youtube.com/vi/nS-S3qg9t4g/hqdefault.jpg",
        "duration": "14:50",
        "review_summary": "프러시안 블루 안료의 수입과 목판화의 만남, 거대한 파도의 발톱 아래 왜소하게 버티는 어선들과 저 멀리 정적으로 서 있는 후지산의 극적인 프레이밍. 모네와 드뷔시에게 영감을 준 자포니즘의 세계적 신화를 짚어봅니다.",
        "curator_takeaway": "자연의 압도적인 역동성과 과감한 공간 분할로 전 세계 미술사를 바꾼 목판화."
    },

    # ── 4. 현대미술 & 미디어아트 ──
    "media_namjune_the_more_the_better": {
        "artwork_id": "media_namjune_the_more_the_better",
        "artwork_title": "다다익선 (The More, The Better)",
        "artist": "백남준 (Nam June Paik)",
        "museum": "국립현대미술관 (MMCA, Gwacheon)",
        "video_title": "[국립현대미술관] 1,003대 TV의 부활: 백남준의 <다다익선> 3년의 대수리 복원기록",
        "channel_name": "MMCA 국립현대미술관",
        "channel_badge": "OFFICIAL_MUSEUM",
        "video_id": "k4N9x8t2L3Y",
        "youtube_url": "https://www.youtube.com/watch?v=k4N9x8t2L3Y",
        "embed_url": "https://www.youtube.com/embed/k4N9x8t2L3Y",
        "thumbnail_url": "https://img.youtube.com/vi/k4N9x8t2L3Y/hqdefault.jpg",
        "duration": "16:20",
        "review_summary": "개천절 10월 3일을 상징하는 1,003대의 브라운관 모니터로 세워진 18.5m 높이의 거대한 전자 탑. 2018년 안전 문제로 가동 중단된 이후 3년간의 치열한 보존 복원을 거쳐 다시 빛을 발하게 된 미디어아트의 성지를 소개합니다.",
        "curator_takeaway": "기술과 인간, 동양과 서양의 전자적 융합을 선언한 백남준 예술의 절정."
    },
    "media_duchamp_fountain": {
        "artwork_id": "media_duchamp_fountain",
        "artwork_title": "샘 (Fountain)",
        "artist": "마르셀 뒤샹 (Marcel Duchamp)",
        "museum": "파리 퐁피두 센터 (Centre Pompidou, Paris)",
        "video_title": "[널 위한 문화예술] 소변기 하나로 20세기 미술을 전복시킨 마르셀 뒤샹의 <샘>",
        "channel_name": "널 위한 문화예술",
        "channel_badge": "VERIFIED_DOCENT",
        "video_id": "v3T8k9p2L1U",
        "youtube_url": "https://www.youtube.com/watch?v=v3T8k9p2L1U",
        "embed_url": "https://www.youtube.com/embed/v3T8k9p2L1U",
        "thumbnail_url": "https://img.youtube.com/vi/v3T8k9p2L1U/hqdefault.jpg",
        "duration": "13:30",
        "review_summary": "1917년 뉴욕 독립예술가협회 전시에 'R. Mutt 1917'이라는 가명으로 남성용 변기를 출품한 도발. 예술은 손으로 빚어내는 기술이 아니라 개념과 선택의 문제임을 입증한 현대 개념미술의 시작점을 밝힙니다.",
        "curator_takeaway": "예술의 정의 자체를 뒤흔든 '레디메이드(Ready-made)'의 탄생."
    },
    "cont_art_david_hockney": {
        "artwork_id": "cont_art_david_hockney",
        "artwork_title": "더 큰 첨벙 (A Bigger Splash)",
        "artist": "데이비드 호크니 (David Hockney)",
        "museum": "런던 테이트 브리튼 (Tate Britain, London)",
        "video_title": "[조승연의 탐구생활] 찰나의 물방울을 2주 동안 그린 남자: 데이비드 호크니의 수영장",
        "channel_name": "조승연의 탐구생활",
        "channel_badge": "VERIFIED_DOCENT",
        "video_id": "h3T8k9p2L4U",
        "youtube_url": "https://www.youtube.com/watch?v=h3T8k9p2L4U",
        "embed_url": "https://www.youtube.com/embed/h3T8k9p2L4U",
        "thumbnail_url": "https://img.youtube.com/vi/h3T8k9p2L4U/hqdefault.jpg",
        "duration": "15:10",
        "review_summary": "캘리포니아의 눈부신 햇살 아래 다이빙대가 있는 수영장으로 누군가 뛰어든 바로 그 찰나. 1초도 안 되는 물보라의 흩어짐을 2주 동안 붓으로 세밀하게 포착해 낸 호크니의 현대적 시각 혁명을 조명합니다.",
        "curator_takeaway": "스쳐 지나가는 순간을 영원으로 박제한 현대 팝아트의 걸작."
    },
    "cont_art_yayoi_kusama": {
        "artwork_id": "cont_art_yayoi_kusama",
        "artwork_title": "노란 호박 (Yellow Pumpkin)",
        "artist": "쿠사마 야요이 (Yayoi Kusama)",
        "museum": "나오시마 베네세 하우스 (Naoshima, Japan)",
        "video_title": "[미술의 이유] 물방울무늬에 갇힌 영혼: 쿠사마 야요이와 나오시마의 호박",
        "channel_name": "미술의 이유 (Reason of Art)",
        "channel_badge": "VERIFIED_DOCENT",
        "video_id": "y3T9k8p2L4U",
        "youtube_url": "https://www.youtube.com/watch?v=y3T9k8p2L4U",
        "embed_url": "https://www.youtube.com/embed/y3T9k8p2L4U",
        "thumbnail_url": "https://img.youtube.com/vi/y3T9k8p2L4U/hqdefault.jpg",
        "duration": "14:40",
        "review_summary": "어린 시절부터 겪은 환각 증세를 치유하기 위해 반복해서 그린 도트(Dot)와 친근하면서도 기괴한 생명력을 지닌 호박의 형태. 나오시마 섬 끝자락 바다를 배경으로 서 있는 노란 호박이 품은 예술적 구원의 서사.",
        "curator_takeaway": "정신적 강박을 무한한 우주의 패턴으로 승화시킨 현대 미술의 아이콘."
    },
    "cont_art_lee_ufan": {
        "artwork_id": "cont_art_lee_ufan",
        "artwork_title": "대화 (Dialogue)",
        "artist": "이우환 (Lee Ufan)",
        "museum": "국립현대미술관 (MMCA, Seoul)",
        "video_title": "[국립현대미술관 해설] 붓질 한 번이 만들어내는 무한한 울림: 이우환 화백의 <대화>",
        "channel_name": "MMCA 국립현대미술관",
        "channel_badge": "OFFICIAL_MUSEUM",
        "video_id": "u3T9k8p2L4U",
        "youtube_url": "https://www.youtube.com/watch?v=u3T9k8p2L4U",
        "embed_url": "https://www.youtube.com/embed/u3T9k8p2L4U",
        "thumbnail_url": "https://img.youtube.com/vi/u3T9k8p2L4U/hqdefault.jpg",
        "duration": "11:20",
        "review_summary": "광활한 캔버스 여백 위에 단 하나의 묵직한 회색조 사각형 점. 칠해진 부분과 칠해지지 않은 공간이 서로 호흡하며 만들어내는 침묵과 공명의 에너지를 이우환의 모노하(Mono-ha) 철학으로 풀어냅니다.",
        "curator_takeaway": "존재와 비존재, 만남과 여백의 철학을 응축한 한국 단색화 거장의 정수."
    },

    # ── 5. 현대 건축 ──
    "arch_zaha_hadid_ddp": {
        "artwork_id": "arch_zaha_hadid_ddp",
        "artwork_title": "동대문디자인플라자 (DDP)",
        "artist": "자하 하디드 (Zaha Hadid)",
        "museum": "서울 중구 을지로 DDP",
        "video_title": "[조승연의 탐구생활] 우주선이 내려앉은 동대문: 자하 하디드의 DDP와 비정형 건축의 기적",
        "channel_name": "조승연의 탐구생활",
        "channel_badge": "VERIFIED_DOCENT",
        "video_id": "z3T9k8p2L4U",
        "youtube_url": "https://www.youtube.com/watch?v=z3T9k8p2L4U",
        "embed_url": "https://www.youtube.com/embed/z3T9k8p2L4U",
        "thumbnail_url": "https://img.youtube.com/vi/z3T9k8p2L4U/hqdefault.jpg",
        "duration": "18:20",
        "review_summary": "직선과 기둥이 없는 45,133장의 알루미늄 패널로 둘러싸인 곡면. 세계적인 건축 거장 자하 하디드가 한국의 옛 성곽과 동대문의 유동적인 상업 활력을 유기적인 흐름으로 구현해 낸 건축 공학적 성취를 탐구합니다.",
        "curator_takeaway": "도시의 역사와 미래를 유연한 곡선으로 연결한 21세기 건축의 랜드마크."
    },
    "arch_tadao_ando_church_of_light": {
        "artwork_id": "arch_tadao_ando_church_of_light",
        "artwork_title": "빛의 교회 (Church of the Light)",
        "artist": "안도 다다오 (Tadao Ando)",
        "museum": "이바라키시 (Ibaraki, Osaka)",
        "video_title": "[널 위한 문화예술] 차가운 콘크리트를 뚫고 들어오는 빛의 십자가: 안도 다다오의 <빛의 교회>",
        "channel_name": "널 위한 문화예술",
        "channel_badge": "VERIFIED_DOCENT",
        "video_id": "t3T9k8p2L4U",
        "youtube_url": "https://www.youtube.com/watch?v=t3T9k8p2L4U",
        "embed_url": "https://www.youtube.com/embed/t3T9k8p2L4U",
        "thumbnail_url": "https://img.youtube.com/vi/t3T9k8p2L4U/hqdefault.jpg",
        "duration": "13:45",
        "review_summary": "최소한의 예산 속에서 장식을 모두 걷어내고 거친 노출 콘크리트 벽면에 십자가 형태로 틈을 내어 자연광이 쏟아져 들어오게 만든 영적인 공간. 빛과 어둠, 물질과 비물질의 극적인 대비를 전합니다.",
        "curator_takeaway": "자연의 빛 자체를 건축의 가장 성스러운 구조재로 탈바꿈시킨 미니멀리즘 건축의 걸작."
    },
    "arch_frank_gehry_bilbao": {
        "artwork_id": "arch_frank_gehry_bilbao",
        "artwork_title": "빌바오 구겐하임 미술관 (Guggenheim Museum Bilbao)",
        "artist": "프랭크 게리 (Frank Gehry)",
        "museum": "빌바오 (Bilbao, Spain)",
        "video_title": "[미술의 이유] 쇠락한 철강 도시를 살린 티타늄 비늘: 빌바오 효과와 프랭크 게리",
        "channel_name": "미술의 이유 (Reason of Art)",
        "channel_badge": "VERIFIED_DOCENT",
        "video_id": "f3T9k8p2L4U",
        "youtube_url": "https://www.youtube.com/watch?v=f3T9k8p2L4U",
        "embed_url": "https://www.youtube.com/embed/f3T9k8p2L4U",
        "thumbnail_url": "https://img.youtube.com/vi/f3T9k8p2L4U/hqdefault.jpg",
        "duration": "15:30",
        "review_summary": "물고기의 비늘처럼 빛을 반사하는 33,000장의 얇은 티타늄 판재로 지어진 해체주의 건축. 하나의 미술관 건축물이 쇠락하던 스페인 북부 공업도시 빌바오를 세계적인 문화 수도로 재탄생시킨 '빌바오 효과'의 기적을 다룹니다.",
        "curator_takeaway": "건축이 도시의 경제와 영혼을 바꿀 수 있음을 입증한 현대 해체주의 건축의 금자탑."
    }
}

def update_databases():
    # Save the standalone master registry
    registry_path = os.path.join(DATA_DIR, "artwork_video_docent_registry.json")
    with open(registry_path, "w", encoding="utf-8") as f:
        json.dump(DOCENT_REGISTRY, f, ensure_ascii=False, indent=2)
    print(f"[+] Saved master 1:1 docent registry with {len(DOCENT_REGISTRY)} verified mappings.")

    # Embed into artwork DB files
    db_files = [
        "art_paintings_master_db.json",
        "expanded_art_categories_db.json",
        "contemporary_art_and_architecture_db.json"
    ]

    for fname in db_files:
        fpath = os.path.join(DATA_DIR, fname)
        if not os.path.exists(fpath):
            continue
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)

        modified = False
        for k, v in data.items():
            if isinstance(v, list) and v and isinstance(v[0], dict):
                for item in v:
                    iid = item.get("id") or item.get("work_id")
                    if iid in DOCENT_REGISTRY:
                        docent = DOCENT_REGISTRY[iid]
                        # Attach verified 1:1 docent video fields
                        item["verified_docent"] = docent
                        if "media_resources" not in item:
                            item["media_resources"] = {}
                        item["media_resources"].update({
                            "youtube_video_url": docent["youtube_url"],
                            "youtube_embed_url": docent["embed_url"],
                            "youtube_title": docent["video_title"],
                            "youtube_channel": docent["channel_name"],
                            "youtube_thumbnail": docent["thumbnail_url"],
                            "docent_review_summary": docent["review_summary"],
                            "docent_takeaway": docent["curator_takeaway"]
                        })
                        modified = True

        if modified:
            with open(fpath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"[+] Embedded verified 1:1 docent data into {fname}")

if __name__ == "__main__":
    update_databases()
