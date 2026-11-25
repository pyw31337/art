#!/usr/bin/env python3
"""
scripts/upgrade_admin_html.py
Upgrades admin/index.html and admin.html with:
1. Lucide & Tabler SVG Icon sprite system (Line by default, Solid on hover/focus)
2. Unified .icon styling
3. Replacing emojis in navigation, tabs, headers, buttons, and badges
"""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICONS_SVG = os.path.join(BASE_DIR, "assets", "icons", "icons.svg")

with open(ICONS_SVG, "r", encoding="utf-8") as f:
    icons_sprite = f.read().strip()

targets = [
    os.path.join(BASE_DIR, "admin", "index.html"),
    os.path.join(BASE_DIR, "admin.html")
]

icon_css = """
    /* ── Lucide & Tabler SVG Icon Standard (LDS 18x18, stroke 1.8) ── */
    .icon {
      width: 18px;
      height: 18px;
      display: inline-block;
      vertical-align: -3px;
      stroke: currentColor;
      fill: none;
      stroke-width: 1.8;
      stroke-linecap: round;
      stroke-linejoin: round;
      transition: fill 0.15s ease, stroke 0.15s ease, transform 0.15s ease;
    }
    button:hover .icon,
    button:focus .icon,
    button:active .icon,
    button.active .icon,
    a:hover .icon,
    a:focus .icon,
    a:active .icon,
    .icon:hover,
    .icon:focus,
    .icon.active {
      fill: currentColor;
    }
"""

for target_path in targets:
    if not os.path.exists(target_path):
        continue
    with open(target_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Add CSS
    if ".icon {" not in content:
        content = content.replace("</style>", icon_css + "\n  </style>")

    # 2. Add SVG Sprite
    if '<svg xmlns="http://www.w3.org/2000/svg" style="display: none;">' not in content:
        content = content.replace("<body>", f"<body>\n\n  <!-- Unified Tabler & Lucide SVG Icons -->\n  {icons_sprite}\n")

    # 3. Replace header / nav / tabs
    content = content.replace('<div class="hero-badge">🏛️</div>', '<div class="hero-badge"><svg class="icon" style="width:22px;height:22px;"><use href="#i-museum"></use></svg></div>')
    content = content.replace('<span>⚡ 데일리 파이프라인 즉시 구동</span>', '<svg class="icon"><use href="#i-zap"></use></svg> <span>데일리 파이프라인 즉시 구동</span>')
    content = content.replace('<span>📊 종합 관제 오버뷰</span>', '<svg class="icon"><use href="#i-chart"></use></svg> <span>종합 관제 오버뷰</span>')
    content = content.replace('<span>🛰️ 수집 장치 & 게이트웨이</span>', '<svg class="icon"><use href="#i-satellite"></use></svg> <span>수집 장치 & 게이트웨이</span>')
    content = content.replace('<span>🧬 온톨로지 & 심층 분석 엔진</span>', '<svg class="icon"><use href="#i-layers"></use></svg> <span>온톨로지 & 심층 분석 엔진</span>')
    content = content.replace('<span>📜 실시간 수집 내역 & 원장 스트림</span>', '<svg class="icon"><use href="#i-history"></use></svg> <span>실시간 수집 내역 & 원장 스트림</span>')
    content = content.replace('<span>⚡ 전체 핑 테스트</span>', '<svg class="icon"><use href="#i-refresh"></use></svg> <span>전체 핑 테스트</span>')

    # Card and section titles
    content = content.replace('<span>🛰️ 실시간 게이트웨이 및 크롤러 핑 상태</span>', '<svg class="icon"><use href="#i-satellite"></use></svg> <span>실시간 게이트웨이 및 크롤러 핑 상태</span>')
    content = content.replace('<span>📖 8대 휴먼 스토리 분포</span>', '<svg class="icon"><use href="#i-book"></use></svg> <span>8대 휴먼 스토리 분포</span>')
    content = content.replace('<span>🎬 연동 명화 해설 채널</span>', '<svg class="icon"><use href="#i-video"></use></svg> <span>연동 명화 해설 채널</span>')
    content = content.replace('<span>🛰️ 렛츠아트 활성 수집 장치 및 크롤러 아키텍처 상세 사양</span>', '<svg class="icon"><use href="#i-satellite"></use></svg> <span>렛츠아트 활성 수집 장치 및 크롤러 아키텍처 상세 사양</span>')
    content = content.replace('<span>📖 인간 중심 8대 스토리 텍소노미 분류 원장 (총 7,978점)</span>', '<svg class="icon"><use href="#i-book"></use></svg> <span>인간 중심 8대 스토리 텍소노미 분류 원장 (총 7,978점)</span>')
    content = content.replace('<span>🕵️ 핸드메이커 & 캔버스 비밀 발굴 원장 (X-Ray & Scandal)</span>', '<svg class="icon"><use href="#i-sparkles"></use></svg> <span>핸드메이커 & 캔버스 비밀 발굴 원장 (X-Ray & Scandal)</span>')
    content = content.replace('<span>🌸 4계절 온톨로지 분포</span>', '<svg class="icon"><use href="#i-sun"></use></svg> <span>4계절 온톨로지 분포</span>')
    content = content.replace('<span>🎨 7대 테마 분포</span>', '<svg class="icon"><use href="#i-palette"></use></svg> <span>7대 테마 분포</span>')
    content = content.replace('<span>📜 실시간 수집 내역 & 원장 레코드 스트림</span>', '<svg class="icon"><use href="#i-history"></use></svg> <span>실시간 수집 내역 & 원장 레코드 스트림</span>')

    # Feed search placeholder
    content = content.replace('placeholder="🔍 작품명, 작가, 소장처, 스토리 키워드 검색..."', 'placeholder="작품명, 작가, 소장처, 스토리 키워드 검색..."')

    # Detail button in drawer
    content = content.replace('<span>📄 전용 작품 페이지 보기 ➔</span>', '<svg class="icon"><use href="#i-frame"></use></svg> <span>전용 작품 상세페이지</span> <svg class="icon" style="width:14px;height:14px;"><use href="#i-external"></use></svg>')

    # Fix clean labels without emoji in JS data tables
    content = content.replace("{ label: '🌸 봄의 찬가', count: '520점 (27.8%)' }", "{ label: '봄의 찬가 (Spring)', count: '520점 (27.8%)' }")
    content = content.replace("{ label: '🍂 가을빛', count: '257점 (13.7%)' }", "{ label: '가을빛 (Autumn)', count: '257점 (13.7%)' }")
    content = content.replace("{ label: '🕊️ 고독과 성찰', count: '1,587점' }", "{ label: '고독과 성찰 (Solitude)', count: '1,587점' }")
    content = content.replace("{ label: '🌙 밤과 별빛', count: '1,060점' }", "{ label: '밤과 별빛 (Night & Stars)', count: '1,060점' }")
    content = content.replace("{ label: '🕵️ 미스터리', count: '876점' }", "{ label: '미스터리 & 음모 (Mystery)', count: '876점' }")
    content = content.replace("{ label: '🇰🇷 한국의 멋', count: '811점' }", "{ label: '한국의 멋 (Korean Heritage)', count: '811점' }")
    content = content.replace("{ label: '🔥 혁명과 자유', count: '575점' }", "{ label: '혁명과 자유 (Revolution)', count: '575점' }")
    content = content.replace("{ label: '💘 세기의 사랑', count: '418점' }", "{ label: '세기의 사랑 (Love)', count: '418점' }")
    content = content.replace("{ label: '🌿 야성과 정글', count: '224점' }", "{ label: '야성과 정글 (Nature)', count: '224점' }")

    content = content.replace('`📺 ${media.youtube_title}`', '`<svg class="icon" style="width:14px;height:14px;"><use href="#i-video"></use></svg> ${media.youtube_title}`')
    content = content.replace('showToast("🛰️ 전체 8개 게이트웨이 핑 검사 중... 전 채널 100% 정상 (지연시간 <45ms)");', 'showToast("전체 8개 게이트웨이 핑 검사 중... 전 채널 100% 정상 (지연시간 <45ms)");')

    with open(target_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[+] Upgraded {target_path}")
