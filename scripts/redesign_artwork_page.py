#!/usr/bin/env python3
"""
scripts/redesign_artwork_page.py
Robust substring replacement for artwork.html:
1. Replaces CSS from 'PARALLAX BOTTOM CONTENT SHEET' to 'PRESENTATION GALLERY — FULLSCREEN'
2. Replaces HTML from '<div class="content-sheet-inner">' to 'PRESENTATION GALLERY — FULLSCREEN'
3. Replaces JS from '// 3. Multimedia Docent Hub' to '// 4. Setup Presentation Mode Data'
"""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTWORK_PATH = os.path.join(BASE_DIR, "artwork.html")

with open(ARTWORK_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# ── 1. NEW CSS ──
new_css = """/* ========================================================
       PARALLAX BOTTOM CONTENT SHEET — LUXURY EDITORIAL NOIR
       ======================================================== */
    .content-sheet-container {
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
    }

    /* Curatorial Header Block */
    .curatorial-header {
      margin-bottom: 24px;
    }
    .curatorial-badge-row {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
      margin-bottom: 12px;
    }
    .curatorial-breadcrumb {
      font-family: var(--lds-font-mono);
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.08em;
      color: #2563eb;
      text-transform: uppercase;
      background: #eff6ff;
      padding: 3px 10px;
      border-radius: 16px;
      border: 1px solid #dbeafe;
    }
    .artwork-title-main {
      font-size: 34px;
      font-weight: 800;
      color: #0f172a;
      letter-spacing: -0.8px;
      line-height: 1.25;
      margin-bottom: 4px;
    }
    .artwork-title-en {
      font-size: 16px;
      color: #64748b;
      font-weight: 400;
      font-style: italic;
      margin-bottom: 16px;
    }
    .artist-credit-pill {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 6px 14px;
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 20px;
      font-size: 13.5px;
      color: #1e293b;
    }
    .artist-credit-pill strong {
      font-weight: 700;
    }

    /* Modern Specification 4-Pill Grid */
    .artwork-spec-grid {
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
    }

    /* AI Voice Docent Station (Refined) */
    .voice-docent-station {
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 16px;
      padding: 16px 20px;
      background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
      border-radius: 10px;
      color: #ffffff;
      margin: 4px 0 12px;
      box-shadow: 0 4px 14px rgba(15, 23, 42, 0.12);
    }
    .voice-play-btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: #2563eb;
      color: #ffffff;
      border: none;
      border-radius: 20px;
      padding: 7px 16px;
      font-size: 12.5px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .voice-play-btn:hover {
      background: #1d4ed8;
      transform: translateY(-1px);
    }
    .voice-status-group {
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 12px;
      color: #cbd5e1;
    }
    .voice-soundwave {
      display: inline-flex;
      align-items: center;
      gap: 3px;
      height: 14px;
    }
    .voice-bar {
      width: 3px;
      height: 6px;
      background: #60a5fa;
      border-radius: 1px;
      transition: height 0.15s ease;
    }
    .voice-soundwave.active .voice-bar {
      animation: soundwave-pulse 1s infinite alternate ease-in-out;
    }
    @keyframes soundwave-pulse {
      0% { height: 4px; }
      100% { height: 14px; }
    }
    .voice-speed-group {
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .voice-rate-btn {
      background: rgba(255,255,255,0.1);
      border: 1px solid rgba(255,255,255,0.15);
      color: #cbd5e1;
      padding: 3px 8px;
      border-radius: 4px;
      font-size: 11px;
      cursor: pointer;
    }
    .voice-rate-btn.active {
      background: #2563eb;
      color: #ffffff;
      border-color: #2563eb;
    }

    /* Behind-the-Scenes Secret Feature (Amber Luxury) */
    .behind-investigation-card {
      background: linear-gradient(135deg, #fffdfa 0%, #fffbeb 100%);
      border: 1px solid #fde68a;
      border-left: 4px solid #d97706;
      border-radius: 10px;
      padding: 24px 28px;
    }
    .behind-inv-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 8px;
    }
    .behind-inv-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-family: var(--lds-font-mono);
      font-size: 11px;
      font-weight: 700;
      color: #b45309;
      letter-spacing: 0.05em;
      text-transform: uppercase;
    }
    .behind-inv-source {
      font-size: 11px;
      color: #92400e;
    }
    .behind-inv-title {
      font-size: 18px;
      font-weight: 700;
      color: #78350f;
      margin-bottom: 10px;
    }
    .behind-inv-text {
      font-size: 14px;
      line-height: 1.8;
      color: #451a03;
    }

    /* Editorial Story Spotlight (Blue Silk) */
    .editorial-story-card {
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-left: 4px solid #2563eb;
      border-radius: 10px;
      padding: 24px 28px;
    }
    .editorial-story-tag {
      font-family: var(--lds-font-mono);
      font-size: 11px;
      font-weight: 700;
      color: #2563eb;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      margin-bottom: 6px;
    }
    .editorial-story-title {
      font-size: 18px;
      font-weight: 700;
      color: #0f172a;
      margin-bottom: 8px;
    }
    .editorial-story-body {
      font-size: 14px;
      line-height: 1.8;
      color: #334155;
    }

    /* Curatorial Analysis & Historical Sections */
    .article-headline {
      font-size: 18px;
      font-weight: 700;
      color: #0f172a;
      margin-bottom: 12px;
      letter-spacing: -0.3px;
    }
    .curator-quote-box {
      border-left: 3px solid #64748b;
      padding: 18px 22px;
      background: #f8fafc;
      border-radius: 0 8px 8px 0;
      font-size: 14px;
      line-height: 1.85;
      color: #1e293b;
    }

    /* Color Palette */
    .palette-flat-grid {
      display: flex;
      gap: 12px;
      align-items: center;
      flex-wrap: wrap;
      margin-top: 14px;
    }
    .palette-item {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 6px 12px;
      border: 1px solid #e2e8f0;
      border-radius: 6px;
      background: #ffffff;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .palette-item:hover {
      border-color: #94a3b8;
      transform: translateY(-1px);
    }
    .palette-color {
      width: 18px;
      height: 18px;
      border-radius: 4px;
      border: 1px solid rgba(0,0,0,0.12);
    }
    .palette-hex {
      font-family: var(--lds-font-mono);
      font-size: 11.5px;
      color: #475569;
      font-weight: 600;
    }

    /* ========================================================
       MULTIMEDIA DOCENT CINEMA HUB
       ======================================================== */
    .docent-cinema-section {
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 12px;
      padding: 32px 36px;
      box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.03);
    }
    @media (max-width: 768px) {
      .docent-cinema-section { padding: 22px 20px; }
    }
    .docent-cinema-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
    }
    .docent-cinema-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-family: var(--lds-font-mono);
      font-size: 11px;
      font-weight: 700;
      color: #ef4444;
      letter-spacing: 0.05em;
    }
    .video-cinema-wrap {
      position: relative;
      width: 100%;
      padding-top: 56.25%;
      border-radius: 10px;
      overflow: hidden;
      background: #000000;
      box-shadow: 0 10px 30px -4px rgba(0,0,0,0.25);
      margin-bottom: 14px;
    }
    .video-cinema-wrap iframe {
      position: absolute;
      top: 0; left: 0;
      width: 100%; height: 100%;
      border: none;
    }
    .docent-video-title {
      font-size: 15px;
      font-weight: 700;
      color: #0f172a;
      line-height: 1.4;
      margin-bottom: 18px;
    }
    .docent-cinema-channel-tag {
      color: #ef4444;
      font-weight: 800;
      margin-right: 6px;
    }

    /* 1:1 Verified Docent Analysis Card */
    .docent-analysis-box {
      margin: 18px 0;
      padding: 20px 22px;
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
    }
    .docent-analysis-header {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 11.5px;
      font-family: var(--lds-font-mono);
      color: #b91c1c;
      letter-spacing: 0.04em;
      margin-bottom: 8px;
      font-weight: 700;
    }
    .docent-analysis-summary {
      font-size: 13.5px;
      line-height: 1.75;
      color: #1e293b;
      margin-bottom: 12px;
    }
    .docent-curator-quote {
      border-left: 3px solid #2563eb;
      padding: 10px 14px;
      font-size: 12.5px;
      line-height: 1.65;
      color: #1e3a8a;
      background: #eff6ff;
      border-radius: 0 6px 6px 0;
    }

    /* ========================================================
       CLEAN PLATFORM DOCK (DE-DUPLICATED & IMMERSIVE)
       ======================================================== */
    .platform-dock-header {
      font-size: 13px;
      font-weight: 700;
      color: #475569;
      margin-bottom: 12px;
      letter-spacing: -0.1px;
    }
    .platform-dock-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 10px;
    }
    @media (max-width: 768px) {
      .platform-dock-grid { grid-template-columns: repeat(2, 1fr); }
    }
    @media (max-width: 480px) {
      .platform-dock-grid { grid-template-columns: 1fr; }
    }
    .platform-dock-card {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px 14px;
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      text-decoration: none;
      color: #0f172a;
      transition: all 0.18s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .platform-dock-card:hover {
      border-color: #3b82f6;
      background: #ffffff;
      transform: translateY(-2px);
      box-shadow: 0 6px 16px -2px rgba(15, 23, 42, 0.08);
    }
    .dock-meta {
      display: flex;
      flex-direction: column;
      gap: 2px;
      min-width: 0;
    }
    .dock-title {
      font-size: 13px;
      font-weight: 700;
      color: #0f172a;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .dock-sub {
      font-size: 11px;
      color: #64748b;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .brand-icon {
      width: 22px;
      height: 22px;
      display: inline-block;
      flex-shrink: 0;
    }

    /* Bottom Action Row (De-duplicated & Centered) */
    .bottom-cta-row {
      display: flex;
      gap: 12px;
      align-items: center;
      justify-content: center;
      padding: 16px 0 0;
    }
    .bottom-cta-btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 11px 22px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 600;
      text-decoration: none;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .bottom-cta-btn.primary {
      background: #2563eb;
      color: #ffffff;
      border: 1px solid #1d4ed8;
      box-shadow: 0 2px 8px rgba(37, 99, 235, 0.2);
    }
    .bottom-cta-btn.primary:hover {
      background: #1d4ed8;
      box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3);
      transform: translateY(-1px);
    }
    .bottom-cta-btn.secondary {
      background: #ffffff;
      color: #1e293b;
      border: 1px solid #cbd5e1;
    }
    .bottom-cta-btn.secondary:hover {
      border-color: #94a3b8;
      background: #f8fafc;
    }
"""

# Replace CSS
css_start = content.find("/* ========================================================\n       PARALLAX BOTTOM CONTENT SHEET")
css_end = content.find("/* ========================================================\n       PRESENTATION GALLERY — FULLSCREEN IMMERSIVE CINEMA")
if css_start != -1 and css_end != -1:
    content = content[:css_start] + new_css + "\n    " + content[css_end:]
    print("[+] Replaced content sheet CSS")
else:
    print("[!] Failed to find CSS boundaries")

# ── 2. NEW HTML INNER ──
new_html_inner = """<div class="content-sheet-inner">

      <!-- ========================================================
           CARD 1: MASTERPIECE OVERVIEW & SPECIFICATIONS
           ======================================================== -->
      <div class="museum-sheet-card">
        <div class="curatorial-header">
          <div class="curatorial-badge-row">
            <span class="curatorial-breadcrumb" id="sheetBreadcrumb">인류 문화유산 아카이브</span>
          </div>
          <h1 class="artwork-title-main" id="sheetTitleKr">작품명</h1>
          <div class="artwork-title-en" id="sheetTitleEn">Artwork Title</div>
          <div class="artist-credit-pill">
            <svg class="icon"><use href="#i-user"></use></svg>
            <strong id="sheetArtistKr">작가명</strong>
            <span id="sheetArtistEn" style="color:#64748b;">(Artist)</span>
          </div>
        </div>

        <!-- 4-Pill Modern Specification Grid -->
        <div class="artwork-spec-grid">
          <div class="spec-pill">
            <span class="spec-label">제작 연도</span>
            <span class="spec-val" id="specYear">연도 정보</span>
          </div>
          <div class="spec-pill">
            <span class="spec-label">기법 & 재료</span>
            <span class="spec-val" id="specMedium">재질 정보</span>
          </div>
          <div class="spec-pill">
            <span class="spec-label">작품 규격</span>
            <span class="spec-val" id="specDimensions">규격 정보</span>
          </div>
          <div class="spec-pill">
            <span class="spec-label">소장처</span>
            <span class="spec-val" id="specMuseum">소장처 정보</span>
          </div>
        </div>

        <!-- AI Audio Docent Station -->
        <div class="voice-docent-station">
          <button class="voice-play-btn" onclick="toggleVoiceDocent()">
            <span id="voicePlayIcon"><svg class="icon"><use href="#i-mic"></use></svg></span>
            <span id="sheetVoiceBtnText">음성 도슨트 재생</span>
          </button>
          <div class="voice-status-group">
            <div class="voice-soundwave" id="voiceSoundwave">
              <span class="voice-bar"></span>
              <span class="voice-bar"></span>
              <span class="voice-bar"></span>
              <span class="voice-bar"></span>
            </div>
            <span class="voice-status-label" id="voiceStatusLabel">명화의 역사와 도상학적 스토리를 음성으로 안내합니다</span>
          </div>
          <div class="voice-speed-group">
            <button class="voice-rate-btn" data-rate="0.9" onclick="setVoiceRate(0.9)">0.9x</button>
            <button class="voice-rate-btn active" data-rate="1.0" onclick="setVoiceRate(1.0)">1.0x</button>
            <button class="voice-rate-btn" data-rate="1.2" onclick="setVoiceRate(1.2)">1.2x</button>
          </div>
        </div>
      </div>

      <!-- ========================================================
           CARD 2: BEHIND STORIES & STORY TAXONOMY
           ======================================================== -->
      <!-- Behind Story Feature (Amber Luxury) -->
      <div class="behind-investigation-card" id="behindSecretCard" style="display:none;">
        <div class="behind-inv-header">
          <span class="behind-inv-badge">
            <svg class="icon" style="width:13px; height:13px;"><use href="#i-sparkles"></use></svg>
            캔버스 비하인드 조사 보고서
          </span>
          <span class="behind-inv-source" id="behindSecretSource"></span>
        </div>
        <div class="behind-inv-title" id="behindSecretTitle">캔버스 밑에 감춰진 비밀과 복원 비화</div>
        <div class="behind-inv-text" id="behindSecretContent"></div>
      </div>

      <!-- Human Story Taxonomy Feature (Blue Silk) -->
      <div class="editorial-story-card" id="storyCard">
        <div class="editorial-story-tag" id="storyTag">HUMAN STORY TAXONOMY</div>
        <div class="editorial-story-title" id="storyHeaderTitle">인간의 삶과 유대감을 투영한 명화</div>
        <div class="editorial-story-body" id="storyDescription">
          이 작품은 인간의 삶과 관계성에서 중요한 테마를 담고 있으며, 깊은 정서적 교감과 시대적 울림을 전해줍니다.
        </div>
      </div>

      <!-- ========================================================
           CARD 3: CURATORIAL COMMENTARY & COLOR PALETTE
           ======================================================== -->
      <div class="museum-sheet-card">
        <h2 class="article-headline">도상학 및 큐레이터 심층 해설</h2>
        <div class="curator-quote-box" id="curatorCommentary">
          작품 해설을 불러오는 중입니다...
        </div>

        <div id="historicalSection" style="display:none; margin-top:24px;">
          <h2 class="article-headline">시대적 배경과 미술사적 의의</h2>
          <div class="curator-quote-box" id="historicalContent" style="border-left-color:#059669; background:#f0fdf4;"></div>
        </div>

        <div style="margin-top:28px;">
          <h2 class="article-headline" style="font-size:15px;">대표 시각 컬러 팔레트</h2>
          <div class="palette-flat-grid" id="paletteSwatches"></div>
        </div>
      </div>

      <!-- ========================================================
           CARD 4: MULTIMEDIA DOCENT CINEMA HUB
           ======================================================== -->
      <div class="docent-cinema-section" id="docentHubSection">
        <div class="docent-cinema-header">
          <span class="docent-cinema-badge">
            <span style="width:7px; height:7px; border-radius:50%; background:#ef4444; display:inline-block;"></span>
            1:1 OFFICIAL VIDEO DOCENT
          </span>
          <span class="lds-mono" style="font-size:11px; color:#64748b;">100% VERIFIED LECTURE</span>
        </div>

        <!-- 16:9 Cinema Player -->
        <div class="video-cinema-wrap" id="videoWrapper">
          <iframe id="docentYoutubeIframe" src="" title="Video Docent" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
        </div>
        <div class="docent-video-title" id="docentVideoTitle">명화 해설 영상</div>

        <!-- 1:1 Precision Docent Review & Curator Analysis -->
        <div class="docent-analysis-box" id="docentAnalysisBox" style="display:none;">
          <div class="docent-analysis-header">
            <svg class="icon" style="width:14px; height:14px; color:#ef4444;"><use href="#i-sparkles"></use></svg>
            <span id="docentAnalysisChannel">공인 도슨트 심층 해설</span>
            <span style="color:#cbd5e1;">|</span>
            <span id="docentAnalysisDuration"></span>
          </div>
          <div class="docent-analysis-summary" id="docentAnalysisSummary"></div>
          <div class="docent-curator-quote" id="docentCuratorQuote"></div>
        </div>

        <!-- Clean De-duplicated Platform Dock Grid -->
        <div class="platform-dock-header">관련 플랫폼 자료 및 탐색 허브</div>
        <div class="platform-dock-grid" id="platformLinksGrid">
          <!-- Dynamically populated via JS -->
        </div>
      </div>

      <!-- ========================================================
           CARD 5: BOTTOM ACTION ROW (CLEAN & CENTERED)
           ======================================================== -->
      <div class="bottom-cta-row">
        <button class="bottom-cta-btn primary" onclick="enterPresentationMode()">
          <svg class="icon"><use href="#i-frame"></use></svg>
          <span>디지털 액자 전체화면</span>
        </button>
        <a href="index.html" class="bottom-cta-btn secondary">
          <svg class="icon"><use href="#i-arrow-left"></use></svg>
          <span>아카이브 홈</span>
        </a>
      </div>

    </div>
  </div>"""

html_start = content.find('<div class="content-sheet-inner">')
html_end = content.find('<!-- ========================================================\n       PRESENTATION GALLERY')
if html_start != -1 and html_end != -1:
    content = content[:html_start] + new_html_inner + "\n\n  " + content[html_end:]
    print("[+] Replaced content sheet HTML")
else:
    print("[!] Failed to find HTML boundaries")

# ── 3. NEW JS DOCENT RENDERING ──
new_js_docent = """// 3. Multimedia Docent Hub (1:1 Exact Artwork Match & Clean De-duplicated Dock)
      const media = item.media_resources || {};
      const docent = item.verified_docent || (videoDocentRegistry ? (videoDocentRegistry[item.id] || videoDocentRegistry[item.work_id]) : null);
      const docentIframe = document.getElementById('docentYoutubeIframe');
      const docentTitle = document.getElementById('docentVideoTitle');
      const analysisBox = document.getElementById('docentAnalysisBox');

      const videoId = (docent && docent.video_id) || media.youtube_video_id || "sdQQjbPqbm4";
      docentIframe.src = `https://www.youtube-nocookie.com/embed/${videoId}`;
      
      if (docent) {
        // Strip duplicate channel name from title if present
        let cleanTitle = docent.video_title || '';
        if (docent.channel_name && cleanTitle.includes(docent.channel_name)) {
          cleanTitle = cleanTitle.replace(`[${docent.channel_name}]`, '').replace(docent.channel_name, '').trim();
        }
        cleanTitle = cleanTitle.replace(/^[\[\(]?[^\]\)]*[\]\)]?\s*[:\-]?\s*/, '').trim() || docent.video_title;
        docentTitle.innerHTML = `<span class="docent-cinema-channel-tag">[${docent.channel_name}]</span> ${cleanTitle}`;
        
        if (analysisBox) {
          analysisBox.style.display = 'block';
          document.getElementById('docentAnalysisChannel').textContent = `${docent.channel_name} · 1:1 작품 전용 해설`;
          document.getElementById('docentAnalysisDuration').textContent = `영상 러닝타임 ${docent.duration || '약 15분'}`;
          document.getElementById('docentAnalysisSummary').textContent = docent.review_summary || '';
          document.getElementById('docentCuratorQuote').innerHTML = `<strong>큐레이터 시선:</strong> ${docent.curator_takeaway || ''}`;
        }
      } else {
        docentTitle.textContent = media.youtube_title || `${item.artist_name_kr} 명화 해설`;
        if (analysisBox) analysisBox.style.display = 'none';
      }

      // Clean De-duplicated 9 Platform Dock Grid (No redundant arrows or words)
      const queryEnc = encodeURIComponent(`${item.title_kr} ${item.artist_name_kr || ''}`);
      const grid = document.getElementById('platformLinksGrid');
      grid.innerHTML = `
        <a href="${(docent && docent.youtube_url) || media.youtube_video_url || 'https://www.youtube.com/results?search_query=' + queryEnc}" target="_blank" class="platform-dock-card" title="YouTube 1:1 풀영상 해설">
          <svg class="brand-icon"><use href="#i-brand-youtube"></use></svg>
          <div class="dock-meta">
            <span class="dock-title">YouTube</span>
            <span class="dock-sub">1:1 심층 풀영상</span>
          </div>
        </a>
        <a href="${media.channel_shorts_url || 'https://www.youtube.com/results?search_query=' + queryEnc + '+shorts'}" target="_blank" class="platform-dock-card" title="Shorts 1분 클립">
          <svg class="brand-icon"><use href="#i-brand-shorts"></use></svg>
          <div class="dock-meta">
            <span class="dock-title">Shorts</span>
            <span class="dock-sub">서정욱 미술토크</span>
          </div>
        </a>
        <a href="${media.channel_reason_of_art || 'https://www.youtube.com/@Reason_Of_Art/videos'}" target="_blank" class="platform-dock-card" title="미술의 이유">
          <svg class="brand-icon"><use href="#i-brand-reason-of-art"></use></svg>
          <div class="dock-meta">
            <span class="dock-title">미술의 이유</span>
            <span class="dock-sub">비하인드 분석</span>
          </div>
        </a>
        <a href="https://search.naver.com/search.naver?where=video&query=${queryEnc}" target="_blank" class="platform-dock-card" title="네이버 동영상">
          <svg class="brand-icon"><use href="#i-brand-naver"></use></svg>
          <div class="dock-meta">
            <span class="dock-title">네이버 TV</span>
            <span class="dock-sub">클립 & 미디어</span>
          </div>
        </a>
        <a href="https://tv.kakao.com/search?q=${queryEnc}" target="_blank" class="platform-dock-card" title="카카오TV">
          <svg class="brand-icon"><use href="#i-brand-kakao"></use></svg>
          <div class="dock-meta">
            <span class="dock-title">카카오TV</span>
            <span class="dock-sub">테마 동영상</span>
          </div>
        </a>
        <a href="${media.instagram_channel_url || 'https://www.instagram.com/behind_canvas_stories_kr/'}" target="_blank" class="platform-dock-card" title="Instagram Behind Stories">
          <svg class="brand-icon"><use href="#i-brand-instagram"></use></svg>
          <div class="dock-meta">
            <span class="dock-title">Instagram</span>
            <span class="dock-sub">캔버스 스토리</span>
          </div>
        </a>
        <a href="https://www.tiktok.com/search?q=${queryEnc}" target="_blank" class="platform-dock-card" title="TikTok 1분 도슨트">
          <svg class="brand-icon"><use href="#i-brand-tiktok"></use></svg>
          <div class="dock-meta">
            <span class="dock-title">TikTok</span>
            <span class="dock-sub">1분 도슨트</span>
          </div>
        </a>
        <a href="https://vimeo.com/search?q=${queryEnc}" target="_blank" class="platform-dock-card" title="Vimeo 예술 다큐멘터리">
          <svg class="brand-icon"><use href="#i-brand-vimeo"></use></svg>
          <div class="dock-meta">
            <span class="dock-title">Vimeo</span>
            <span class="dock-sub">예술 다큐</span>
          </div>
        </a>
        <a href="${media.channel_nulart || 'https://www.youtube.com/@nulart'}" target="_blank" class="platform-dock-card" title="널 위한 문화예술">
          <svg class="brand-icon"><use href="#i-brand-nulart"></use></svg>
          <div class="dock-meta">
            <span class="dock-title">널 위한 문화예술</span>
            <span class="dock-sub">인문학 특강</span>
          </div>
        </a>
      `;"""

js_start = content.find("// 3. Multimedia Docent Hub")
js_end = content.find("// 4. Setup Presentation Mode Data")
if js_start != -1 and js_end != -1:
    content = content[:js_start] + new_js_docent + "\n\n      " + content[js_end:]
    print("[+] Replaced JS docent hub rendering")
else:
    print("[!] Failed to find JS boundaries")

with open(ARTWORK_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("[+] artwork.html successfully updated!")
