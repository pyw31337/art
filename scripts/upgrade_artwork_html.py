#!/usr/bin/env python3
"""
scripts/upgrade_artwork_html.py
Upgrades artwork.html with:
1. Lucide & Tabler SVG Icon sprite system (Line by default, Solid on hover/focus)
2. 1:1 Precision Docent Video embed & In-depth Review summary
3. Robust local + R2 image fallback logic
4. Universal database resolution across all 4 databases
"""

import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTWORK_HTML = os.path.join(BASE_DIR, "artwork.html")
ICONS_SVG = os.path.join(BASE_DIR, "assets", "icons", "icons.svg")

with open(ICONS_SVG, "r", encoding="utf-8") as f:
    icons_sprite = f.read().strip()

with open(ARTWORK_HTML, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add CSS for .icon if not present
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

    /* 1:1 Verified Docent Analysis Card */
    .docent-analysis-box {
      margin-top: 14px;
      padding: 16px 18px;
      background: #fafbfc;
      border: 1px solid var(--lds-divider-line);
      border-radius: var(--lds-radius-sm);
    }
    .docent-analysis-header {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 11px;
      font-family: var(--lds-font-mono);
      color: #b91c1c;
      letter-spacing: 0.05em;
      margin-bottom: 8px;
      font-weight: 700;
    }
    .docent-analysis-summary {
      font-size: 13px;
      line-height: 1.7;
      color: var(--lds-text-strong);
      margin-bottom: 10px;
    }
    .docent-curator-quote {
      border-left: 3px solid #2563eb;
      padding-left: 12px;
      font-size: 12px;
      line-height: 1.6;
      color: #1e3a8a;
      background: #eff6ff;
      padding-top: 8px;
      padding-bottom: 8px;
      border-radius: 0 4px 4px 0;
    }
"""

if ".icon {" not in content:
    content = content.replace("</style>", icon_css + "\n  </style>")

# 2. Insert SVG Sprite right after <body>
if '<svg xmlns="http://www.w3.org/2000/svg" style="display: none;">' not in content:
    content = content.replace("<body>", f"<body>\n\n  <!-- Unified Tabler & Lucide SVG Icons -->\n  {icons_sprite}\n")

# 3. Replace nav buttons with SVG icons
old_top_nav = """      <div class="nav-brand-group">
        <a href="index.html" class="nav-back-link">
          <span>← 렛츠아트 (전체 아카이브)</span>
        </a>
      </div>
      <div class="nav-actions">
        <a href="admin" class="lds-nav-btn" style="text-decoration:none;" title="수집 & 분석 관제 어드민">
          <span>⚙️ 관제</span>
        </a>
        <button class="lds-nav-btn" id="btnVoiceDocentNav" onclick="toggleVoiceDocent()" title="AI 한국어 음성 도슨트 해설">
          <span id="voicePulseIcon" style="display:inline-block; width:6px; height:6px; border-radius:50%; background:#3b82f6;"></span>
          <span id="voiceNavText">AI 음성 도슨트</span>
        </button>
        <button class="lds-nav-btn primary" id="btnLaunchPresentation" onclick="enterPresentationMode()" title="화면 꺼짐 방지 디지털 액자 전체화면 감상">
          <span style="display:inline-block; width:6px; height:6px; border-radius:50%; background:#10b981;"></span>
          <span>디지털 액자 모드</span>
        </button>
        <button class="lds-nav-btn" onclick="scrollToDocent()" title="영상 해설 영역으로 바로 이동">
          <span>영상 도슨트</span>
        </button>
      </div>"""

new_top_nav = """      <div class="nav-brand-group">
        <a href="index.html" class="nav-back-link">
          <svg class="icon"><use href="#i-arrow-left"></use></svg>
          <span>렛츠아트 홈 (아카이브)</span>
        </a>
      </div>
      <div class="nav-actions">
        <a href="museum.html" class="lds-nav-btn" style="text-decoration:none;" title="글로벌 10대 미술관 탐색">
          <svg class="icon"><use href="#i-museum"></use></svg>
          <span>미술관</span>
        </a>
        <a href="artist.html" class="lds-nav-btn" style="text-decoration:none;" title="시대의 거장 아카이브">
          <svg class="icon"><use href="#i-user"></use></svg>
          <span>거장</span>
        </a>
        <a href="admin" class="lds-nav-btn" style="text-decoration:none;" title="수집 & 분석 관제 어드민">
          <svg class="icon"><use href="#i-settings"></use></svg>
          <span>관제</span>
        </a>
        <button class="lds-nav-btn" id="btnVoiceDocentNav" onclick="toggleVoiceDocent()" title="AI 한국어 음성 도슨트 해설">
          <svg class="icon"><use href="#i-mic"></use></svg>
          <span id="voiceNavText">음성 도슨트</span>
        </button>
        <button class="lds-nav-btn primary" id="btnLaunchPresentation" onclick="enterPresentationMode()" title="화면 꺼짐 방지 디지털 액자 전체화면 감상">
          <svg class="icon"><use href="#i-frame"></use></svg>
          <span>디지털 액자</span>
        </button>
        <button class="lds-nav-btn" onclick="scrollToDocent()" title="영상 해설 영역으로 바로 이동">
          <svg class="icon"><use href="#i-video"></use></svg>
          <span>영상 도슨트</span>
        </button>
      </div>"""

content = content.replace(old_top_nav, new_top_nav)

# 4. Replace toggle subtitle button
old_toggle_btn = """    <button class="toggle-subtitle-btn" id="btnToggleSubtitle" onclick="toggleLowerThird()">
      <span id="toggleSubtitleIcon">💬</span>
      <span id="toggleSubtitleText">자막 숨기기</span>
    </button>"""

new_toggle_btn = """    <button class="toggle-subtitle-btn" id="btnToggleSubtitle" onclick="toggleLowerThird()">
      <span id="toggleSubtitleIcon"><svg class="icon"><use href="#i-message"></use></svg></span>
      <span id="toggleSubtitleText">자막 숨기기</span>
    </button>"""

content = content.replace(old_toggle_btn, new_toggle_btn)

# 5. Replace Voice Docent Station Play Button
old_voice_btn = """          <button class="voice-play-btn" onclick="toggleVoiceDocent()">
            <span id="voicePlayIcon">🎙️</span>
            <span id="sheetVoiceBtnText">AI 한국어 음성 도슨트 해설 재생</span>
          </button>"""

new_voice_btn = """          <button class="voice-play-btn" onclick="toggleVoiceDocent()">
            <span id="voicePlayIcon"><svg class="icon"><use href="#i-mic"></use></svg></span>
            <span id="sheetVoiceBtnText">AI 한국어 음성 도슨트 해설 재생</span>
          </button>"""

content = content.replace(old_voice_btn, new_voice_btn)

# 6. Replace Presentation HUD Buttons
old_pres_btns = """      <div style="display:flex; align-items:center; gap:12px;">
        <button class="pres-hud-btn" onclick="exitPresentationMode()">
          <span>✕ 나가기</span>
        </button>
        <span class="lds-mono" style="font-size:11px; color:#10b981; display:inline-flex; align-items:center; gap:6px;">
          <span style="width:6px; height:6px; border-radius:50%; background:#10b981;"></span>
          <span id="wakeLockText">화면 꺼짐 방지 활성 (WakeLock)</span>
        </span>
      </div>

      <div style="display:flex; align-items:center; gap:8px;">
        <button class="pres-hud-btn" id="btnVoiceDocentPres" onclick="toggleVoiceDocent()" title="AI 한국어 음성 도슨트 해설">
          <span id="voicePresIcon">🎙️</span>
          <span id="voicePresText">AI 해설</span>
        </button>
        <button class="pres-hud-btn active" id="btnTourToggle" onclick="toggleAutoTour()">
          <span>🎥 카메라 모션 On</span>
        </button>
        <button class="pres-hud-btn" onclick="zoomIn()" title="확대 (+)">
          <span>➕</span>
        </button>
        <button class="pres-hud-btn" onclick="zoomOut()" title="축소 (-)">
          <span>➖</span>
        </button>
        <button class="pres-hud-btn" onclick="resetZoomPan()" title="원래 크기로 초기화">
          <span>↺ 리셋</span>
        </button>
      </div>"""

new_pres_btns = """      <div style="display:flex; align-items:center; gap:12px;">
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
      </div>"""

content = content.replace(old_pres_btns, new_pres_btns)

# 7. Upgrade Multimedia Docent Hub HTML with Analysis Card container
old_docent_hub = """        <!-- 16:9 Video Player -->
        <div class="video-cinema-wrap" id="videoWrapper">
          <iframe id="docentYoutubeIframe" src="" title="Video Docent" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
        </div>
        <div class="docent-video-title" id="docentVideoTitle">📺 명화 해설 영상</div>

        <!-- Unified 9 Platform Direct Access Links -->
        <div class="platform-links-bar" id="platformLinksGrid">
          <!-- Dynamically populated via JS -->
        </div>"""

new_docent_hub = """        <!-- 16:9 Video Player -->
        <div class="video-cinema-wrap" id="videoWrapper">
          <iframe id="docentYoutubeIframe" src="" title="Video Docent" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
        </div>
        <div class="docent-video-title" id="docentVideoTitle">명화 해설 영상</div>

        <!-- 1:1 Precision Docent Review & Curator Analysis -->
        <div class="docent-analysis-box" id="docentAnalysisBox" style="display:none;">
          <div class="docent-analysis-header">
            <svg class="icon" style="width:14px; height:14px; color:#ef4444;"><use href="#i-sparkles"></use></svg>
            <span id="docentAnalysisChannel">공인 도슨트 심층 해설</span>
            <span style="color:var(--lds-divider-line);">|</span>
            <span id="docentAnalysisDuration"></span>
          </div>
          <div class="docent-analysis-summary" id="docentAnalysisSummary"></div>
          <div class="docent-curator-quote" id="docentCuratorQuote"></div>
        </div>

        <!-- Unified 9 Platform Direct Access Links -->
        <div class="platform-links-bar" id="platformLinksGrid">
          <!-- Dynamically populated via JS -->
        </div>"""

content = content.replace(old_docent_hub, new_docent_hub)

# 8. Update Javascript logic for fetching and rendering docent & artwork
old_fetch_js = """    async function fetchArtworkData() {
      try {
        const res1 = await fetch('data/art_paintings_master_db.json?v=' + Date.now()).then(r => r.json());
        const list1 = res1.featured_masterpieces || [];
        let found = list1.find(a => (a.id === targetId || a.work_id === targetId));

        if (!found) {
          try {
            const exp = await fetch('data/expanded_art_categories_db.json?v=' + Date.now()).then(r => r.json());
            const expList = [
              ...(exp.sculptures || []),
              ...(exp.photography || []),
              ...(exp.decorative_arts || []),
              ...(exp.media_and_installation || [])
            ];
            found = expList.find(a => (a.id === targetId || a.work_id === targetId));
          } catch (e) {}
        }

        if (!found) {
          const resDg = await fetch('data/digital_gallery_master_db.json?v=' + Date.now()).then(r => r.json());
          const dgList = resDg.artworks || [];
          found = dgList.find(a => (a.id === targetId || a.work_id === targetId));
        }

        if (!found && list1.length > 0) {
          found = list1[0];
        }

        if (found) {
          currentArtwork = found;
          renderArtworkDetails(found);
          if (autoPresentation) {
            enterPresentationMode();
          }
        }
      } catch (err) {
        console.error("Failed to load artwork data:", err);
      }
    }"""

new_fetch_js = """    let videoDocentRegistry = {};

    async function fetchArtworkData() {
      try {
        // Load 1:1 Video Docent Registry first
        try {
          videoDocentRegistry = await fetch('data/artwork_video_docent_registry.json?v=' + Date.now()).then(r => r.json());
        } catch(e) {
          console.warn("Docent registry load error:", e);
        }

        // 1. Check Master Paintings DB
        const res1 = await fetch('data/art_paintings_master_db.json?v=' + Date.now()).then(r => r.json());
        const list1 = [...(res1.featured_masterpieces || []), ...(res1.featured_paintings || [])];
        let found = list1.find(a => (a.id === targetId || a.work_id === targetId));

        // 2. Check Expanded Art Categories DB
        if (!found) {
          try {
            const exp = await fetch('data/expanded_art_categories_db.json?v=' + Date.now()).then(r => r.json());
            const expList = [
              ...(exp.featured_sculpture || []),
              ...(exp.featured_asian_art || []),
              ...(exp.featured_prints || []),
              ...(exp.featured_photography || []),
              ...(exp.featured_decorative || []),
              ...(exp.featured_media_art || [])
            ];
            found = expList.find(a => (a.id === targetId || a.work_id === targetId));
          } catch (e) {}
        }

        // 3. Check Contemporary Art & Architecture DB
        if (!found) {
          try {
            const cont = await fetch('data/contemporary_art_and_architecture_db.json?v=' + Date.now()).then(r => r.json());
            const contList = [
              ...(cont.featured_contemporary_art || []),
              ...(cont.featured_contemporary_architecture || [])
            ];
            found = contList.find(a => (a.id === targetId || a.work_id === targetId));
          } catch (e) {}
        }

        // 4. Check Digital Gallery Master DB (7858 works)
        if (!found) {
          try {
            const resDg = await fetch('data/digital_gallery_master_db.json?v=' + Date.now()).then(r => r.json());
            const dgList = resDg.artworks || [];
            found = dgList.find(a => (a.id === targetId || a.work_id === targetId));
          } catch(e) {}
        }

        if (!found && list1.length > 0) {
          found = list1[0];
        }

        if (found) {
          // Attach 1:1 docent if present in registry
          const regDocent = videoDocentRegistry[found.id] || videoDocentRegistry[found.work_id];
          if (regDocent) {
            found.verified_docent = regDocent;
          }
          currentArtwork = found;
          renderArtworkDetails(found);
          if (autoPresentation) {
            enterPresentationMode();
          }
        }
      } catch (err) {
        console.error("Failed to load artwork data:", err);
      }
    }"""

content = content.replace(old_fetch_js, new_fetch_js)

# 9. Update renderArtworkDetails docent hub rendering
old_render_docent = """      // 3. Multimedia Docent Hub
      const media = item.media_resources || {};
      const docentIframe = document.getElementById('docentYoutubeIframe');
      const docentTitle = document.getElementById('docentVideoTitle');

      const videoId = media.youtube_video_id || "82Z0HfOkX_0";
      docentIframe.src = `https://www.youtube-nocookie.com/embed/${videoId}`;
      docentTitle.textContent = `📺 ${media.youtube_title || (item.artist_name_kr + ' 명화 세계와 해설')}`;

      // Clean Unified 9 Platform Links
      const grid = document.getElementById('platformLinksGrid');
      grid.innerHTML = `
        <a href="${media.youtube_video_url || media.youtube_search_url}" target="_blank" class="lds-platform-btn">
          <span>▶️ 유튜브 해설 풀영상</span> <span class="arrow">➔</span>
        </a>
        <a href="${media.channel_shorts_url || media.youtube_shorts_search_url}" target="_blank" class="lds-platform-btn">
          <span>⚡ 서정욱 미술토크 Shorts</span> <span class="arrow">➔</span>
        </a>
        <a href="${media.channel_reason_of_art}" target="_blank" class="lds-platform-btn">
          <span>🎨 미술의 이유 채널</span> <span class="arrow">➔</span>
        </a>
        <a href="${media.naver_video_search_url || media.naver_tv_url}" target="_blank" class="lds-platform-btn">
          <span>🟢 네이버 TV·클립 해설</span> <span class="arrow">➔</span>
        </a>
          <span>🟡 다음·카카오TV 영상</span> <span class="arrow">➔</span>
        </a>
        <a href="${media.instagram_channel_url}" target="_blank" class="lds-platform-btn">
          <span>📸 인스타 Behind Stories</span> <span class="arrow">➔</span>
        </a>
        <a href="${media.tiktok_search_url}" target="_blank" class="lds-platform-btn">
          <span>🎵 틱톡 1분 도슨트</span> <span class="arrow">➔</span>
        </a>
        <a href="${media.vimeo_search_url}" target="_blank" class="lds-platform-btn">
          <span>🎬 비메오(Vimeo) 다큐</span> <span class="arrow">➔</span>
        </a>
        <a href="${media.channel_nulart || 'https://www.youtube.com/@nulart'}" target="_blank" class="lds-platform-btn">
          <span>🏛️ 널 위한 문화예술</span> <span class="arrow">➔</span>
        </a>
      `;"""

new_render_docent = """      // 3. Multimedia Docent Hub (1:1 Exact Artwork Match)
      const media = item.media_resources || {};
      const docent = item.verified_docent || (videoDocentRegistry ? (videoDocentRegistry[item.id] || videoDocentRegistry[item.work_id]) : null);
      const docentIframe = document.getElementById('docentYoutubeIframe');
      const docentTitle = document.getElementById('docentVideoTitle');
      const analysisBox = document.getElementById('docentAnalysisBox');

      const videoId = (docent && docent.video_id) || media.youtube_video_id || "82Z0HfOkX_0";
      docentIframe.src = (docent && docent.embed_url) ? docent.embed_url : `https://www.youtube-nocookie.com/embed/${videoId}`;
      
      if (docent) {
        docentTitle.innerHTML = `<span style="color:#ef4444; font-weight:700;">[${docent.channel_name}]</span> ${docent.video_title}`;
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

      // Clean Unified 9 Platform Links with Tabler & Lucide SVG Icons
      const queryEnc = encodeURIComponent(`${item.title_kr} ${item.artist_name_kr || ''}`);
      const grid = document.getElementById('platformLinksGrid');
      grid.innerHTML = `
        <a href="${(docent && docent.youtube_url) || media.youtube_video_url || 'https://www.youtube.com/results?search_query=' + queryEnc}" target="_blank" class="lds-platform-btn">
          <span><svg class="icon"><use href="#i-play"></use></svg> 유튜브 1:1 해설 영상</span> <svg class="icon" style="width:14px;height:14px;"><use href="#i-external"></use></svg>
        </a>
        <a href="${media.channel_shorts_url || 'https://www.youtube.com/results?search_query=' + queryEnc + '+shorts'}" target="_blank" class="lds-platform-btn">
          <span><svg class="icon"><use href="#i-zap"></use></svg> 서정욱 미술토크 Shorts</span> <svg class="icon" style="width:14px;height:14px;"><use href="#i-external"></use></svg>
        </a>
        <a href="${media.channel_reason_of_art || 'https://www.youtube.com/@Reason_Of_Art/videos'}" target="_blank" class="lds-platform-btn">
          <span><svg class="icon"><use href="#i-palette"></use></svg> 미술의 이유 채널</span> <svg class="icon" style="width:14px;height:14px;"><use href="#i-external"></use></svg>
        </a>
        <a href="https://search.naver.com/search.naver?where=video&query=${queryEnc}" target="_blank" class="lds-platform-btn">
          <span><svg class="icon"><use href="#i-video"></use></svg> 네이버 TV·클립 해설</span> <svg class="icon" style="width:14px;height:14px;"><use href="#i-external"></use></svg>
        </a>
        <a href="https://tv.kakao.com/search?q=${queryEnc}" target="_blank" class="lds-platform-btn">
          <span><svg class="icon"><use href="#i-video"></use></svg> 다음·카카오TV 영상</span> <svg class="icon" style="width:14px;height:14px;"><use href="#i-external"></use></svg>
        </a>
        <a href="${media.instagram_channel_url || 'https://www.instagram.com/behind_canvas_stories_kr/'}" target="_blank" class="lds-platform-btn">
          <span><svg class="icon"><use href="#i-camera"></use></svg> 인스타 Behind Stories</span> <svg class="icon" style="width:14px;height:14px;"><use href="#i-external"></use></svg>
        </a>
        <a href="https://www.tiktok.com/search?q=${queryEnc}" target="_blank" class="lds-platform-btn">
          <span><svg class="icon"><use href="#i-film"></use></svg> 틱톡 1분 도슨트</span> <svg class="icon" style="width:14px;height:14px;"><use href="#i-external"></use></svg>
        </a>
        <a href="https://vimeo.com/search?q=${queryEnc}" target="_blank" class="lds-platform-btn">
          <span><svg class="icon"><use href="#i-film"></use></svg> 비메오(Vimeo) 다큐</span> <svg class="icon" style="width:14px;height:14px;"><use href="#i-external"></use></svg>
        </a>
        <a href="${media.channel_nulart || 'https://www.youtube.com/@nulart'}" target="_blank" class="lds-platform-btn">
          <span><svg class="icon"><use href="#i-museum"></use></svg> 널 위한 문화예술</span> <svg class="icon" style="width:14px;height:14px;"><use href="#i-external"></use></svg>
        </a>
      `;"""

content = content.replace(old_render_docent, new_render_docent)

# 10. Fix image fallback to try local webp before fallbackSvg
old_img_fallback = """      // 1. Hero Zone
      const heroImg = document.getElementById('heroArtworkImg');
      heroImg.src = imgUrl;
      heroImg.onerror = () => { heroImg.src = fallbackSvg; };"""

new_img_fallback = """      // 1. Hero Zone with multi-stage fallback
      const heroImg = document.getElementById('heroArtworkImg');
      heroImg.src = imgUrl;
      heroImg.onerror = () => {
        const localFallback = `assets/featured/${item.id}.webp`;
        if (heroImg.src !== localFallback && !heroImg.dataset.failedLocal) {
          heroImg.dataset.failedLocal = "true";
          heroImg.src = localFallback;
        } else {
          heroImg.src = fallbackSvg;
        }
      };"""

content = content.replace(old_img_fallback, new_img_fallback)

# 11. Update lower third toggle function to use SVG
old_toggle_func = """      if (lowerThirdVisible) {
        el.classList.remove('hidden');
        icon.textContent = '💬';
        txt.textContent = '자막 숨기기';
      } else {
        el.classList.add('hidden');
        icon.textContent = '👁️';
        txt.textContent = '자막 켜기';
      }"""

new_toggle_func = """      if (lowerThirdVisible) {
        el.classList.remove('hidden');
        icon.innerHTML = '<svg class="icon"><use href="#i-message"></use></svg>';
        txt.textContent = '자막 숨기기';
      } else {
        el.classList.add('hidden');
        icon.innerHTML = '<svg class="icon"><use href="#i-eye-off"></use></svg>';
        txt.textContent = '자막 켜기';
      }"""

content = content.replace(old_toggle_func, new_toggle_func)

with open(ARTWORK_HTML, "w", encoding="utf-8") as f:
    f.write(content)

print("[+] artwork.html successfully upgraded!")
