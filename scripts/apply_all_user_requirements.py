#!/usr/bin/env python3
import sys, re

def run():
    with open('artwork.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # =========================================================================
    # 1. CSS REPLACEMENTS (Glassmorphism & Anti-Box minimal borders)
    # =========================================================================
    
    # Replace .hero-lower-third-wrap and .lower-third-panel with ultra-clear Glassmorphism
    old_lt_css = """.hero-lower-third-wrap {
      position: absolute;
      bottom: 28px;
      left: 28px;
      right: 28px;
      max-width: 820px;
      margin: 0 auto;
      z-index: 25;
      pointer-events: none;
      transition: opacity 0.3s cubic-bezier(0.16, 1, 0.3, 1), transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .hero-lower-third-wrap.hidden {
      opacity: 0;
      transform: translateY(20px);
      pointer-events: none;
    }

    .lower-third-panel {
      pointer-events: auto;
      background: rgba(10, 14, 22, 0.8);
      backdrop-filter: blur(24px);
      -webkit-backdrop-filter: blur(24px);
      border: 1px solid var(--hairline-dark);
      border-radius: 6px;
      padding: 16px 20px;
      box-shadow: 0 16px 40px rgba(0, 0, 0, 0.6);
      display: flex;
      flex-direction: column;
      gap: 6px;
    }"""

    new_lt_css = """.hero-lower-third-wrap {
      position: absolute;
      bottom: 24px;
      left: 24px;
      right: 24px;
      max-width: 780px;
      margin: 0 auto;
      z-index: 25;
      pointer-events: none;
      transition: opacity 0.3s cubic-bezier(0.16, 1, 0.3, 1), transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .hero-lower-third-wrap.hidden {
      opacity: 0;
      transform: translateY(18px);
      pointer-events: none;
    }

    /* True Airy Glassmorphism: Background artwork shines through cleanly */
    .lower-third-panel {
      pointer-events: auto;
      background: rgba(15, 23, 42, 0.32);
      backdrop-filter: blur(28px) saturate(190%);
      -webkit-backdrop-filter: blur(28px) saturate(190%);
      border: 1px solid rgba(255, 255, 255, 0.16);
      border-radius: 12px;
      padding: 18px 24px;
      box-shadow: 0 16px 40px -8px rgba(0, 0, 0, 0.35);
      display: flex;
      flex-direction: column;
      gap: 6px;
    }"""

    if old_lt_css in html:
        html = html.replace(old_lt_css, new_lt_css)
        print("Updated lower third CSS with Glassmorphism.")
    else:
        print("Warning: old_lt_css exact match not found, applying regex")
        html = re.sub(
            r'\.lower-third-panel\s*\{[^}]+\}',
            """.lower-third-panel {
      pointer-events: auto;
      background: rgba(15, 23, 42, 0.32);
      backdrop-filter: blur(28px) saturate(190%);
      -webkit-backdrop-filter: blur(28px) saturate(190%);
      border: 1px solid rgba(255, 255, 255, 0.16);
      border-radius: 12px;
      padding: 18px 24px;
      box-shadow: 0 16px 40px -8px rgba(0, 0, 0, 0.35);
      display: flex;
      flex-direction: column;
      gap: 6px;
    }""",
            html
        )

    # Replace toggle-subtitle-btn to make it a sleek icon-only button
    old_sub_btn = """.toggle-subtitle-btn {
      position: absolute;
      bottom: 28px;
      right: 28px;
      z-index: 35;
      background: rgba(10, 14, 22, 0.75);
      backdrop-filter: blur(14px);
      -webkit-backdrop-filter: blur(14px);
      border: 1px solid var(--hairline-dark);
      color: #cbd5e1;
      padding: 6px 12px;
      border-radius: 4px;
      font-size: 11.5px;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: all 0.15s ease;
    }
    .toggle-subtitle-btn:hover {
      background: rgba(20, 26, 38, 0.9);
      color: #ffffff;
      border-color: rgba(255, 255, 255, 0.3);
    }"""

    new_sub_btn = """.toggle-subtitle-btn {
      position: absolute;
      bottom: 24px;
      right: 24px;
      z-index: 35;
      width: 42px;
      height: 42px;
      border-radius: 50%;
      background: rgba(15, 23, 42, 0.35);
      backdrop-filter: blur(20px) saturate(180%);
      -webkit-backdrop-filter: blur(20px) saturate(180%);
      border: 1px solid rgba(255, 255, 255, 0.18);
      color: #cbd5e1;
      padding: 0;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.2s cubic-bezier(0.2, 0, 0, 1);
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
    }
    .toggle-subtitle-btn:hover {
      background: rgba(255, 255, 255, 0.18);
      color: #ffffff;
      border-color: rgba(255, 255, 255, 0.4);
      transform: scale(1.06);
    }

    /* Floating Left & Right Navigation Arrows for Artworks */
    .nav-artwork-arrow {
      position: absolute;
      top: 50%;
      transform: translateY(-50%);
      width: 50px;
      height: 50px;
      border-radius: 50%;
      background: rgba(15, 23, 42, 0.32);
      backdrop-filter: blur(24px) saturate(180%);
      -webkit-backdrop-filter: blur(24px) saturate(180%);
      border: 1px solid rgba(255, 255, 255, 0.18);
      color: #ffffff;
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 40;
      cursor: pointer;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.3s ease, transform 0.2s cubic-bezier(0.2, 0, 0, 1), background 0.2s;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
    }
    .nav-artwork-arrow.left { left: 24px; }
    .nav-artwork-arrow.right { right: 24px; }
    .nav-artwork-arrow:hover {
      background: rgba(255, 255, 255, 0.22);
      border-color: rgba(255, 255, 255, 0.45);
      transform: translateY(-50%) scale(1.08);
    }
    .nav-artwork-arrow:active {
      transform: translateY(-50%) scale(0.94);
    }
    .hero-container:hover .nav-artwork-arrow,
    .hero-container.active-nav .nav-artwork-arrow,
    .presentation-overlay:hover .nav-artwork-arrow,
    .presentation-overlay.active-nav .nav-artwork-arrow {
      opacity: 1;
      pointer-events: auto;
    }

    /* Slideshow Countdown Progress Indicator */
    .slideshow-progress-bar {
      position: absolute;
      top: 0;
      left: 0;
      height: 2px;
      background: #3b82f6;
      width: 0%;
      z-index: 101;
      transition: width 0.1s linear;
    }"""

    if old_sub_btn in html:
        html = html.replace(old_sub_btn, new_sub_btn)
        print("Updated toggle subtitle btn CSS and added navigation arrow styles.")

    # Update Content Sheet to Anti-Box minimal borders layout
    old_sheet_css = """.content-sheet-container {
      position: relative;
      z-index: 20;
      margin-top: 100vh;
      background: #fafaf9;
      color: var(--lds-text-body);
      border-top: 1px solid rgba(226, 232, 240, 0.9);
      min-height: 100vh;
      padding: 56px 20px 100px;
    }

    .content-sheet-inner {
      max-width: 900px;
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      gap: 24px;
    }

    /* Museum Editorial Card Base */
    .museum-sheet-card {
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 12px;
      padding: 32px 36px;
      box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.03);
      position: relative;
      overflow: hidden;
    }
    @media (max-width: 768px) {
      .museum-sheet-card { padding: 22px 20px; }
    }"""

    new_sheet_css = """.content-sheet-container {
      position: relative;
      z-index: 20;
      margin-top: 100vh;
      background: #ffffff;
      color: var(--lds-text-body);
      border: none;
      min-height: 100vh;
      padding: 48px 24px 100px;
    }

    .content-sheet-inner {
      max-width: 880px;
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      gap: 40px;
    }

    /* Anti-Box Editorial Museum Section (Minimal borders) */
    .museum-sheet-card {
      background: transparent;
      border: none;
      border-bottom: 1px solid rgba(226, 232, 240, 0.65);
      border-radius: 0;
      padding: 0 0 40px;
      box-shadow: none;
      position: relative;
    }
    @media (max-width: 768px) {
      .museum-sheet-card { padding: 0 0 32px; }
    }"""

    if old_sheet_css in html:
        html = html.replace(old_sheet_css, new_sheet_css)
        print("Updated content sheet to Anti-Box minimal borders.")

    # Flatten .artwork-spec-grid (remove chunky nested box pills)
    old_spec_css = """.artwork-spec-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 12px;
      margin-top: 20px;
    }
    @media (max-width: 640px) {
      .artwork-spec-grid { grid-template-columns: 1fr; }
    }
    .spec-pill {
      display: flex;
      flex-direction: column;
      gap: 3px;
      padding: 12px 16px;
      background: #f8fafc;
      border: 1px solid #edf2f7;
      border-radius: 8px;
      transition: border-color 0.15s ease;
    }
    .spec-pill:hover {
      border-color: #cbd5e1;
    }
    .spec-label {
      font-size: 11px;
      font-weight: 600;
      color: #64748b;
      letter-spacing: 0.03em;
      text-transform: uppercase;
    }
    .spec-val {
      font-size: 13.5px;
      font-weight: 600;
      color: #0f172a;
      line-height: 1.4;
    }"""

    new_spec_css = """.artwork-spec-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 20px;
      margin-top: 24px;
      padding: 20px 0;
      border-top: 1px solid rgba(226, 232, 240, 0.6);
      border-bottom: 1px solid rgba(226, 232, 240, 0.6);
    }
    @media (max-width: 768px) {
      .artwork-spec-grid { grid-template-columns: repeat(2, 1fr); gap: 16px; }
    }
    .spec-pill {
      display: flex;
      flex-direction: column;
      gap: 4px;
      background: transparent;
      border: none;
      padding: 0;
    }
    .spec-label {
      font-size: 11px;
      font-weight: 700;
      color: #94a3b8;
      letter-spacing: 0.06em;
      text-transform: uppercase;
    }
    .spec-val {
      font-size: 14px;
      font-weight: 600;
      color: #0f172a;
      line-height: 1.45;
    }"""

    if old_spec_css in html:
        html = html.replace(old_spec_css, new_spec_css)
        print("Updated artwork spec grid to flat borderless layout.")

    # Remove heavy borders from behind cards and cinema hub
    html = re.sub(
        r'\.docent-cinema-section\s*\{[^}]+\}',
        """.docent-cinema-section {
      background: transparent;
      border: none;
      border-bottom: 1px solid rgba(226, 232, 240, 0.65);
      border-radius: 0;
      padding: 0 0 40px;
      box-shadow: none;
    }""",
        html
    )

    # Presentation mode CSS updates (Glassmorphism & Drag stability)
    old_pres_css = """.pres-canvas-wrap {
      position: absolute;
      inset: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
      cursor: grab;
    }
    .pres-canvas-wrap:active {
      cursor: grabbing;
    }

    .pres-artwork-img {
      max-width: 100%;
      max-height: 100%;
      object-fit: contain;
      transform-origin: center center;
      will-change: transform;
      transition: transform 0.1s ease-out;
    }"""

    new_pres_css = """.pres-canvas-wrap {
      position: absolute;
      inset: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
      cursor: grab;
      touch-action: none;
    }
    .pres-canvas-wrap.is-dragging {
      cursor: grabbing;
    }

    .pres-artwork-img {
      max-width: 100%;
      max-height: 100%;
      object-fit: contain;
      transform-origin: center center;
      will-change: transform;
      user-select: none;
      -webkit-user-drag: none;
      pointer-events: none;
    }"""

    if old_pres_css in html:
        html = html.replace(old_pres_css, new_pres_css)
        print("Updated presentation canvas wrap CSS.")

    # Presentation HUD buttons & Caption Box Glassmorphism
    old_pres_hud = """.pres-hud-btn {
      background: rgba(12, 16, 23, 0.7);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid var(--hairline-dark);
      color: #ffffff;
      padding: 7px 14px;
      border-radius: 4px;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.15s ease;
    }
    .pres-hud-btn:hover {
      background: rgba(22, 28, 40, 0.9);
      border-color: rgba(255, 255, 255, 0.3);
    }
    .pres-hud-btn.active {
      background: var(--lds-brand-600);
      border-color: var(--lds-brand-600);
    }

    .pres-hud-bottom {
      position: absolute;
      bottom: 24px;
      left: 24px;
      right: 24px;
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
      z-index: 100;
      pointer-events: none;
    }

    .pres-caption-box {
      pointer-events: auto;
      max-width: 640px;
      background: rgba(10, 14, 22, 0.85);
      backdrop-filter: blur(24px);
      -webkit-backdrop-filter: blur(24px);
      border: 1px solid var(--hairline-dark);
      border-radius: 4px;
      padding: 14px 18px;
      color: #ffffff;
      box-shadow: 0 16px 40px rgba(0, 0, 0, 0.7);
      transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }"""

    new_pres_hud = """.pres-hud-btn {
      background: rgba(15, 23, 42, 0.35);
      backdrop-filter: blur(20px) saturate(180%);
      -webkit-backdrop-filter: blur(20px) saturate(180%);
      border: 1px solid rgba(255, 255, 255, 0.18);
      color: #ffffff;
      width: 40px;
      height: 40px;
      border-radius: 50%;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 0;
      transition: all 0.2s cubic-bezier(0.2, 0, 0, 1);
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
    }
    .pres-hud-btn:hover {
      background: rgba(255, 255, 255, 0.2);
      border-color: rgba(255, 255, 255, 0.4);
      transform: scale(1.05);
    }
    .pres-hud-btn.active {
      background: #2563eb;
      border-color: #3b82f6;
    }
    .pres-hud-btn.pill {
      width: auto;
      height: 38px;
      border-radius: 20px;
      padding: 0 14px;
      gap: 6px;
      font-family: var(--lds-font-mono);
      font-size: 11.5px;
    }

    .pres-hud-bottom {
      position: absolute;
      bottom: 24px;
      left: 24px;
      right: 24px;
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
      z-index: 100;
      pointer-events: none;
    }

    /* Glassmorphism for Presentation Mode Caption: artwork visible behind */
    .pres-caption-box {
      pointer-events: auto;
      max-width: 600px;
      background: rgba(15, 23, 42, 0.32);
      backdrop-filter: blur(28px) saturate(190%);
      -webkit-backdrop-filter: blur(28px) saturate(190%);
      border: 1px solid rgba(255, 255, 255, 0.16);
      border-radius: 12px;
      padding: 16px 22px;
      color: #ffffff;
      box-shadow: 0 16px 40px -8px rgba(0, 0, 0, 0.4);
      transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }"""

    if old_pres_hud in html:
        html = html.replace(old_pres_hud, new_pres_hud)
        print("Updated presentation HUD and caption box CSS.")

    # =========================================================================
    # 2. HTML STRUCTURE UPDATES
    # =========================================================================

    # In heroZone: Add left/right navigation arrows, and update subtitle toggle button
    old_hero_nav_btn = """    <!-- Lower-Third Subtitle Toggle Button -->
    <button class="toggle-subtitle-btn" id="btnToggleSubtitle" onclick="toggleLowerThird()">
      <span id="toggleSubtitleIcon"><svg class="icon"><use href="#i-message"></use></svg></span>
      <span id="toggleSubtitleText">자막 숨기기</span>
    </button>"""

    new_hero_nav_btn = """    <!-- Left & Right Artwork Navigation Arrows (Touch & Hover) -->
    <button class="nav-artwork-arrow left" id="heroNavPrev" onclick="navigateArtwork(-1)" title="이전 작품 (←)">
      <svg class="icon" style="width:22px; height:22px;"><use href="#i-chevron-left"></use></svg>
    </button>
    <button class="nav-artwork-arrow right" id="heroNavNext" onclick="navigateArtwork(1)" title="다음 작품 (→)">
      <svg class="icon" style="width:22px; height:22px;"><use href="#i-chevron-right"></use></svg>
    </button>

    <!-- Lower-Third Subtitle Toggle Button (Icon-Only Clean Design) -->
    <button class="toggle-subtitle-btn" id="btnToggleSubtitle" onclick="toggleLowerThird()" title="자막 켜기/끄기">
      <span id="toggleSubtitleIcon"><svg class="icon"><use href="#i-message"></use></svg></span>
    </button>"""

    if old_hero_nav_btn in html:
        html = html.replace(old_hero_nav_btn, new_hero_nav_btn)
        print("Added hero navigation arrows and icon-only subtitle toggle.")

    # In Presentation Mode:
    # 1) Remove "화면 꺼짐 방지 활성 (WakeLock)" verbose text
    # 2) Replace verbose text buttons with icon-only buttons
    # 3) Add interval slideshow button
    # 4) Add left/right arrows for presentation mode
    old_pres_html = """    <!-- HUD Top -->
    <div class="pres-hud-top">
      <div style="display:flex; align-items:center; gap:12px;">
        <button class="pres-hud-btn" onclick="exitPresentationMode()">
          <svg class="icon"><use href="#i-close"></use></svg>
          <span>나가기</span>
        </button>
        <span class="lds-mono" style="font-size:11px; color:#10b981; display:inline-flex; align-items:center; gap:6px;">
          <span style="width:6px; height:6px; border-radius:50%; background:#10b981;"></span>
          <span id="wakeLockText">화면 꺼짐 방지 활성 (WakeLock)</span>
        </span>
      </div>

      <div style="display:flex; align-items:center; gap:8px;">
        <button class="pres-hud-btn" id="btnVoiceDocentPres" onclick="toggleVoiceDocent()" title="AI 한국어 음성 도슨트 해설">
          <svg class="icon"><use href="#i-mic"></use></svg>
          <span id="voicePresText">AI 해설</span>
        </button>
        <button class="pres-hud-btn active" id="btnTourToggle" onclick="toggleAutoTour()">
          <svg class="icon"><use href="#i-camera"></use></svg>
          <span>카메라 투어</span>
        </button>
        <button class="pres-hud-btn" onclick="zoomIn()" title="확대 (+)">
          <svg class="icon"><use href="#i-zoom-in"></use></svg>
        </button>
        <button class="pres-hud-btn" onclick="zoomOut()" title="축소 (-)">
          <svg class="icon"><use href="#i-zoom-out"></use></svg>
        </button>
        <button class="pres-hud-btn" onclick="resetZoomPan()" title="원래 크기로 초기화">
          <svg class="icon"><use href="#i-refresh"></use></svg>
        </button>
      </div>
    </div>

    <!-- HUD Bottom -->
    <div class="pres-hud-bottom">
      <div class="pres-caption-box" id="presLowerThird">
        <div class="lt-meta-header" style="margin-bottom:4px;">
          <span class="lt-dot"></span>
          <span id="presMuseumBadge">소장처</span>
          <span>·</span>
          <span id="presStoryBadge">스토리</span>
        </div>
        <div style="font-size:18px; font-weight:700; margin-bottom:2px;" id="presTitle">작품 제목</div>
        <div style="font-size:12.5px; color:#cbd5e1;" id="presArtist">작가명</div>
        <div style="font-size:12px; color:#94a3b8; margin-top:6px; line-height:1.5;" id="presDesc"></div>
      </div>

      <div style="pointer-events:auto;">
        <button class="pres-hud-btn" onclick="togglePresSubtitle()">
          <svg class="icon"><use href="#i-message"></use></svg>
          <span>자막 켜기/끄기</span>
        </button>
      </div>
    </div>"""

    new_pres_html = """    <!-- Slideshow Progress Bar -->
    <div class="slideshow-progress-bar" id="slideshowProgressBar"></div>

    <!-- Left & Right Artwork Navigation Arrows in Fullscreen Presentation -->
    <button class="nav-artwork-arrow left" id="presNavPrev" onclick="navigateArtwork(-1)" title="이전 작품 (←)">
      <svg class="icon" style="width:24px; height:24px;"><use href="#i-chevron-left"></use></svg>
    </button>
    <button class="nav-artwork-arrow right" id="presNavNext" onclick="navigateArtwork(1)" title="다음 작품 (→)">
      <svg class="icon" style="width:24px; height:24px;"><use href="#i-chevron-right"></use></svg>
    </button>

    <!-- HUD Top (Clean Icon-Only & Interval Controls) -->
    <div class="pres-hud-top">
      <div style="display:flex; align-items:center; gap:10px;">
        <button class="pres-hud-btn" onclick="exitPresentationMode()" title="전체화면 종료 (ESC)">
          <svg class="icon"><use href="#i-close"></use></svg>
        </button>
        <!-- Discreet WakeLock status pulse (No noisy verbose text) -->
        <span id="wakeLockDot" style="width:8px; height:8px; border-radius:50%; background:#10b981; box-shadow:0 0 10px #10b981; display:inline-block;" title="화면 꺼짐 방지 활성화 (WakeLock)"></span>
      </div>

      <div style="display:flex; align-items:center; gap:8px;">
        <!-- Auto-Advance Slideshow Interval Selector (OFF / 10s / 15s / 20s) -->
        <button class="pres-hud-btn pill" id="btnSlideshowInterval" onclick="cycleSlideshowInterval()" title="자동 작품 넘김 시간 (클릭하여 10초/15초/20초 설정)">
          <svg class="icon"><use href="#i-clock"></use></svg>
          <span id="intervalBadge">OFF</span>
        </button>
        <button class="pres-hud-btn" id="btnVoiceDocentPres" onclick="toggleVoiceDocent()" title="AI 한국어 음성 도슨트">
          <svg class="icon"><use href="#i-mic"></use></svg>
        </button>
        <button class="pres-hud-btn active" id="btnTourToggle" onclick="toggleAutoTour()" title="카메라 모션 투어">
          <svg class="icon"><use href="#i-camera"></use></svg>
        </button>
        <button class="pres-hud-btn" onclick="zoomIn()" title="확대 (+)">
          <svg class="icon"><use href="#i-zoom-in"></use></svg>
        </button>
        <button class="pres-hud-btn" onclick="zoomOut()" title="축소 (-)">
          <svg class="icon"><use href="#i-zoom-out"></use></svg>
        </button>
        <button class="pres-hud-btn" onclick="resetZoomPan()" title="원래 크기 및 중앙 정렬">
          <svg class="icon"><use href="#i-refresh"></use></svg>
        </button>
      </div>
    </div>

    <!-- HUD Bottom -->
    <div class="pres-hud-bottom">
      <div class="pres-caption-box" id="presLowerThird">
        <div class="lt-meta-header" style="margin-bottom:4px;">
          <span class="lt-dot"></span>
          <span id="presMuseumBadge">소장처</span>
          <span>·</span>
          <span id="presStoryBadge">스토리</span>
        </div>
        <div style="font-size:18px; font-weight:700; margin-bottom:2px;" id="presTitle">작품 제목</div>
        <div style="font-size:12.5px; color:#cbd5e1;" id="presArtist">작가명</div>
        <div style="font-size:12px; color:#94a3b8; margin-top:6px; line-height:1.5;" id="presDesc"></div>
      </div>

      <div style="pointer-events:auto;">
        <button class="pres-hud-btn" onclick="togglePresSubtitle()" title="자막 켜기/끄기">
          <svg class="icon"><use href="#i-message"></use></svg>
        </button>
      </div>
    </div>"""

    if old_pres_html in html:
        html = html.replace(old_pres_html, new_pres_html)
        print("Updated presentation mode HTML with clean icon-only controls and slideshow pill.")

    # =========================================================================
    # 3. JAVASCRIPT LOGIC UPDATES
    # =========================================================================

    # Find the script section and upgrade:
    # 1) Artwork catalog collection & navigateArtwork(-1 / 1)
    # 2) Slideshow timer (10s, 15s, 20s, OFF)
    # 3) Hover/Touch active-nav timer
    # 4) Pointer-event based 60fps drag & zoom with correct coordinate math

    js_marker_start = "    let currentArtwork = null;"
    js_new_logic = """    let currentArtwork = null;
    let artworkCatalog = [];
    let currentCatalogIndex = 0;
    let wakeLock = null;
    let lowerThirdVisible = true;
    let presLowerThirdVisible = true;
    let isAutoTour = true;

    // Slideshow Auto-Advance State
    let slideshowIntervalSeconds = 0; // 0 = OFF, 10, 15, 20
    let slideshowTimer = null;
    let slideshowProgressAnim = null;
    let slideshowStartTime = 0;

    // Interactive Zoom & Pan State (Rock-solid 60fps Pointer-based)
    let zoomScale = 1.0;
    let panX = 0;
    let panY = 0;
    let isPointerDragging = false;
    let dragStartScreenX = 0, dragStartScreenY = 0;
    let dragStartPanX = 0, dragStartPanY = 0;
    let activePointers = new Map();
    let initialPinchDistance = 0;
    let initialPinchScale = 1.0;

    // Nav arrows auto-hide timer on hover/touch
    let navHideTimeout = null;

    function triggerNavActivity() {
      const hero = document.getElementById('heroZone');
      const pres = document.getElementById('presOverlay');
      if (hero) hero.classList.add('active-nav');
      if (pres) pres.classList.add('active-nav');

      if (navHideTimeout) clearTimeout(navHideTimeout);
      navHideTimeout = setTimeout(() => {
        if (hero) hero.classList.remove('active-nav');
        if (pres) pres.classList.remove('active-nav');
      }, 3500);
    }

    ['mousemove', 'touchstart', 'click'].forEach(evt => {
      window.addEventListener(evt, triggerNavActivity, { passive: true });
    });"""

    html = html.replace(js_marker_start, js_new_logic, 1)

    # Replace loadArtworkData to populate artworkCatalog and handle smooth switching
    old_load_fn = """        // Fallback only if absolutely no artwork matched
        if (!found && list1.length > 0) {
          found = list1[0];
        }

        if (found) {
          // Attach 1:1 verified docent
          const regDocent = videoDocentRegistry[found.id] || videoDocentRegistry[found.work_id];
          if (regDocent) {
            found.verified_docent = regDocent;
          }
          currentArtwork = found;
          renderArtworkDetails(found);
          if (autoPresentation) {
            enterPresentationMode();
          }
        }"""

    new_load_fn = """        // Build full unified catalog for next/previous navigation
        const combined = [];
        const seenIds = new Set();
        [...list1, ...expList, ...contList, ...(resDg ? (resDg.artworks || []) : [])].forEach(item => {
          const cid = item.id || item.work_id;
          if (cid && !seenIds.has(cid)) {
            seenIds.add(cid);
            combined.push(item);
          }
        });
        artworkCatalog = combined;

        // Fallback only if absolutely no artwork matched
        if (!found && artworkCatalog.length > 0) {
          found = artworkCatalog[0];
        }

        if (found) {
          currentCatalogIndex = artworkCatalog.findIndex(a => (a.id === found.id || a.work_id === found.work_id));
          if (currentCatalogIndex < 0) currentCatalogIndex = 0;

          // Attach 1:1 verified docent
          const regDocent = videoDocentRegistry[found.id] || videoDocentRegistry[found.work_id];
          if (regDocent) {
            found.verified_docent = regDocent;
          }
          currentArtwork = found;
          renderArtworkDetails(found);
          if (autoPresentation) {
            enterPresentationMode();
          }
        }"""

    # We need to make sure expList and contList are in scope
    # Let's inspect how expList and contList were defined in loadArtworkData
    # Let's write a clean version of loadArtworkData that collects all lists cleanly
    
    with open('artwork.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Base CSS and HTML replacements applied.")

if __name__ == '__main__':
    run()
