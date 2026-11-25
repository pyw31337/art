#!/usr/bin/env python3
import re

with open('artwork.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add CSS for Verified Resource Cards and Empty State
new_css = """
    /* ========================================================
       VERIFIED-ONLY PLATFORM RESOURCES DOCK (CONTENT-DRIVEN)
       ======================================================== */
    .platform-dock-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 14px;
    }
    .platform-dock-header-title {
      font-size: 13.5px;
      font-weight: 700;
      color: #0f172a;
      letter-spacing: -0.2px;
    }
    .platform-dock-header-count {
      font-family: var(--lds-font-mono);
      font-size: 11px;
      font-weight: 700;
      color: #2563eb;
      background: #eff6ff;
      padding: 2px 8px;
      border-radius: 12px;
      border: 1px solid #dbeafe;
    }
    .verified-resources-list {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .verified-resource-card {
      background: #f8fafc;
      border: 1px solid rgba(226, 232, 240, 0.7);
      border-radius: 10px;
      padding: 16px 20px;
      transition: all 0.15s ease;
    }
    .verified-resource-card:hover {
      background: #ffffff;
      border-color: #3b82f6;
      box-shadow: 0 4px 16px rgba(15, 23, 42, 0.05);
    }
    .vcard-top {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
      flex-wrap: wrap;
      gap: 8px;
    }
    .vcard-platform-badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-size: 12.5px;
      font-weight: 600;
      color: #1e293b;
    }
    .vcard-badge {
      font-family: var(--lds-font-mono);
      font-size: 10.5px;
      font-weight: 700;
      color: #2563eb;
      background: #eff6ff;
      padding: 2px 8px;
      border-radius: 12px;
      border: 1px solid #dbeafe;
    }
    .vcard-title {
      font-size: 14px;
      font-weight: 700;
      color: #0f172a;
      margin-bottom: 6px;
      line-height: 1.4;
    }
    .vcard-summary {
      font-size: 12.5px;
      color: #475569;
      line-height: 1.6;
      margin-bottom: 12px;
    }
    .vcard-action-btn {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 12px;
      font-weight: 700;
      color: #2563eb;
      text-decoration: none;
      transition: all 0.15s ease;
    }
    .vcard-action-btn:hover {
      color: #1d4ed8;
      transform: translateX(2px);
    }
    .verified-empty-state {
      text-align: center;
      padding: 28px 20px;
      background: #f8fafc;
      border: 1px dashed rgba(226, 232, 240, 0.9);
      border-radius: 10px;
    }
    .verified-hub-footer {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-top: 14px;
      font-size: 11px;
      color: #64748b;
      line-height: 1.5;
      padding: 8px 12px;
      background: #f1f5f9;
      border-radius: 6px;
    }
"""

if '.verified-resource-card' not in html:
    html = html.replace('</style>', new_css + '\n  </style>')

# 2. Update HTML structure for Card 4 multimedia dock
old_cinema_dock_html = """        <!-- Clean De-duplicated Platform Dock Grid -->
        <div class="platform-dock-header">관련 플랫폼 자료 및 탐색 허브</div>
        <div class="platform-dock-grid" id="platformLinksGrid">
          <!-- Dynamically populated via JS -->
        </div>"""

new_cinema_dock_html = """        <!-- Verified Multimedia & Academic Sources Hub (Content-Driven) -->
        <div class="platform-dock-header">
          <span class="platform-dock-header-title">1:1 사전 검증된 외부 해설 및 공식 학술 아카이브</span>
          <span class="platform-dock-header-count" id="verifiedResourceCount">검증 자료 로딩</span>
        </div>
        <div id="platformLinksGrid">
          <!-- Dynamically populated via JS: only verified resources appear -->
        </div>"""

html = html.replace(old_cinema_dock_html, new_cinema_dock_html)

# 3. Replace platformLinksGrid JS generation with 100% verified-only logic
old_js_grid = """      // Clean De-duplicated 9 Platform Dock Grid
      const queryEnc = encodeURIComponent(`${titleKr} ${artistKr}`);
      const grid = document.getElementById('platformLinksGrid');
      if (grid) {
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
        `;
      }"""

new_js_grid = """      // Verified-Only Content-Driven Platform Resources
      const grid = document.getElementById('platformLinksGrid');
      const countBadge = document.getElementById('verifiedResourceCount');
      const verifiedList = (docent && docent.verified_resources) || [];

      // Helper to map platform to proper vector SVG symbol
      const getPlatformIcon = (plat) => {
        if (plat === 'youtube') return '#i-brand-youtube';
        if (plat === 'shorts') return '#i-brand-shorts';
        if (plat === 'museum_official') return '#i-museum';
        if (plat === 'naver_art') return '#i-brand-naver';
        if (plat === 'handmaker') return '#i-sparkles';
        if (plat === 'artinsight') return '#i-book';
        if (plat === 'reason_of_art') return '#i-brand-reason-of-art';
        if (plat === 'nulart') return '#i-brand-nulart';
        return '#i-external';
      };

      if (grid) {
        if (verifiedList.length > 0) {
          if (countBadge) countBadge.textContent = `${verifiedList.length}개 공인 자료 연동`;
          grid.innerHTML = `
            <div class="verified-resources-list">
              ${verifiedList.map(res => `
                <div class="verified-resource-card">
                  <div class="vcard-top">
                    <span class="vcard-platform-badge">
                      <svg class="brand-icon"><use href="${getPlatformIcon(res.platform)}"></use></svg>
                      <span>${res.channel_name}</span>
                    </span>
                    <span class="vcard-badge">${res.badge || '공인 검증'}</span>
                  </div>
                  <div class="vcard-title">${res.title}</div>
                  <div class="vcard-summary">${res.summary}</div>
                  <a href="${res.url}" target="_blank" class="vcard-action-btn" title="외부 공인 원문/영상 바로보기">
                    <span>해당 검증 자료 바로보기</span>
                    <svg class="icon" style="width:13px; height:13px;"><use href="#i-arrow-right"></use></svg>
                  </a>
                </div>
              `).join('')}
            </div>
            <div class="verified-hub-footer">
              <svg class="icon" style="width:14px; height:14px; color:#10b981; flex-shrink:0;"><use href="#i-check"></use></svg>
              <span>렛츠아트는 작품과 직접 관련된 내용이 100% 사전 분석·검증된 공인 미술사 채널 및 학술 자료만 엄선하여 연동합니다. 단순 검색 페이지나 무관한 링크는 제공하지 않습니다.</span>
            </div>
          `;
        } else if (docent && docent.youtube_url) {
          // Fallback single verified docent
          if (countBadge) countBadge.textContent = "1개 공인 자료 연동";
          grid.innerHTML = `
            <div class="verified-resources-list">
              <div class="verified-resource-card">
                <div class="vcard-top">
                  <span class="vcard-platform-badge">
                    <svg class="brand-icon"><use href="#i-brand-youtube"></use></svg>
                    <span>${docent.channel_name}</span>
                  </span>
                  <span class="vcard-badge">1:1 공인 도슨트</span>
                </div>
                <div class="vcard-title">${docent.video_title}</div>
                <div class="vcard-summary">${docent.review_summary || '작품의 도상학적 기법과 미술사적 배경을 다룬 심층 해설입니다.'}</div>
                <a href="${docent.youtube_url}" target="_blank" class="vcard-action-btn" title="YouTube 영상 바로보기">
                  <span>YouTube에서 영상 시청하기</span>
                  <svg class="icon" style="width:13px; height:13px;"><use href="#i-arrow-right"></use></svg>
                </a>
              </div>
            </div>
            <div class="verified-hub-footer">
              <svg class="icon" style="width:14px; height:14px; color:#10b981; flex-shrink:0;"><use href="#i-check"></use></svg>
              <span>렛츠아트는 작품과 직접 관련된 내용이 100% 사전 분석·검증된 공인 미술사 채널 및 학술 자료만 엄선하여 연동합니다.</span>
            </div>
          `;
        } else {
          if (countBadge) countBadge.textContent = "자체 연구 진행 중";
          grid.innerHTML = `
            <div class="verified-empty-state">
              <svg class="icon" style="width:28px; height:28px; color:#3b82f6; margin-bottom:8px;"><use href="#i-sparkles"></use></svg>
              <div style="font-weight:700; font-size:14px; color:#0f172a; margin-bottom:4px;">렛츠아트 자체 큐레이터 해설 및 AI 음성 도슨트 제공 중</div>
              <div style="font-size:12.5px; color:#64748b; line-height:1.6; max-width:540px; margin:0 auto;">외부 공인 미술사 채널 및 박물관 학술 자료를 정밀 분석 및 수집 중이며, 검증된 1:1 자료가 확인되는 대로 즉시 연동됩니다. (단순 검색이나 무관한 링크는 제공하지 않습니다)</div>
            </div>
          `;
        }
      }"""

if old_js_grid in html:
    html = html.replace(old_js_grid, new_js_grid)
    print("Replaced JS grid with verified-only content-driven rendering.")
else:
    print("Error: old_js_grid not found directly. Checking substrings.")

with open('artwork.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Updated artwork.html with verified-only resource cards.")
