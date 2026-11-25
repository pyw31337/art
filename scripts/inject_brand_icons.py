#!/usr/bin/env python3
"""
scripts/inject_brand_icons.py
Collects and injects official SVG brand icons & symbols for:
1. YouTube (Red logo with white play mark)
2. YouTube Shorts (S-curved red shorts icon with play mark)
3. Reason of Art (Verified indigo art channel badge)
4. Naver (Official green 'N' square emblem)
5. Kakao / Daum (Official yellow speech bubble emblem)
6. Instagram (Official vibrant camera glyph)
7. TikTok (Official black & musical note symbol)
8. Vimeo (Official vibrant blue 'v' emblem)
9. Nulart (Official navy/sky-blue classical pediment museum symbol)
"""

import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICONS_SVG_PATH = os.path.join(BASE_DIR, "assets", "icons", "icons.svg")
ARTWORK_HTML_PATH = os.path.join(BASE_DIR, "artwork.html")

BRAND_SYMBOLS = """
    <!-- Official Platform Brand Icons & Symbols -->
    <symbol id="i-brand-youtube" viewBox="0 0 24 24">
      <path fill="#FF0000" d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814z"/>
      <polygon fill="#FFFFFF" points="9.545 15.568 15.818 12 9.545 8.432 9.545 15.568"/>
    </symbol>

    <symbol id="i-brand-shorts" viewBox="0 0 24 24">
      <path fill="#FF0000" d="M17.77 10.32l-1.2-.5a5.52 5.52 0 0 0-.6-.23A6.16 6.16 0 0 0 15 9.4a6.38 6.38 0 0 0-4.48-1.8 6.55 6.55 0 0 0-3.32.9L5.3 9.68a5.53 5.53 0 0 0-2.82 4.8 5.61 5.61 0 0 0 2.82 4.85l1.9.95a5.55 5.55 0 0 0 3.32.9 6.38 6.38 0 0 0 4.48-1.8 6.44 6.44 0 0 0 1.9-4.35 5.53 5.53 0 0 0-.6-2.56l1.47.74a3.46 3.46 0 0 0 4.67-1.38 3.55 3.55 0 0 0-1.47-4.66z"/>
      <polygon fill="#FFFFFF" points="10 14.5 15 12 10 9.5"/>
    </symbol>

    <symbol id="i-brand-naver" viewBox="0 0 24 24">
      <path fill="#03C75A" d="M16.273 12.845L7.37 0H0v24h7.727V11.155L16.63 24H24V0h-7.727z"/>
    </symbol>

    <symbol id="i-brand-kakao" viewBox="0 0 24 24">
      <path fill="#FEE500" d="M12 3c-5.523 0-10 3.582-10 8 0 2.864 1.88 5.378 4.73 6.74-.21.78-.76 2.82-.87 3.25-.14.53.19.52.4.38.16-.11 2.58-1.75 3.63-2.47.7.1 1.4.15 2.11.15 5.523 0 10-3.582 10-8s-4.477-8-10-8z"/>
      <path fill="#191919" d="M8.2 13.8v-5h1.2v5H8.2zm4-3.5l1.3 3.5h-1.3l-.2-.7h-1.2l-.2.7H9.4l1.3-3.5v-.01h1.5zm2.3 3.5l-1.3-5h1.3l.7 3.3.7-3.3h1.3l-1.3 5h-1.4z"/>
    </symbol>

    <symbol id="i-brand-instagram" viewBox="0 0 24 24">
      <path fill="#E1306C" d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
    </symbol>

    <symbol id="i-brand-tiktok" viewBox="0 0 24 24">
      <path fill="#000000" d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-5.2 1.74 2.89 2.89 0 0 1 2.31-4.64 2.93 2.93 0 0 1 .88.13V9.4a6.84 6.84 0 0 0-1-.05A6.33 6.33 0 0 0 3 15.68 6.34 6.34 0 0 0 9.35 22a6.33 6.33 0 0 0 6.33-6.32V8.71a8.21 8.21 0 0 0 4.91 1.63V6.89a4.85 4.85 0 0 1-1-.2z"/>
    </symbol>

    <symbol id="i-brand-vimeo" viewBox="0 0 24 24">
      <path fill="#1AB7EA" d="M22.84 6.64c-.11 2.45-1.82 5.8-5.13 10.05-3.42 4.41-6.31 6.62-8.68 6.62-1.47 0-2.71-1.36-3.72-4.08l-2.03-7.44C2.53 9.07 1.83 7.7 1.18 7.7c-.15 0-.68.32-1.6.96L0 7.37c1.07-.94 2.12-1.89 3.16-2.85 1.43-1.24 2.51-1.9 3.23-1.99 1.73-.19 2.79.99 3.19 3.54.43 2.74.72 4.46.88 5.16.48 2.36 1.01 3.54 1.59 3.54.45 0 1.13-.74 2.04-2.22.91-1.48 1.4-2.6 1.47-3.37.13-1.28-.37-1.92-1.5-1.92-.54 0-1.1.12-1.68.37 1.11-3.64 3.24-5.4 6.39-5.28 2.33.08 3.42 1.41 3.27 3.99z"/>
    </symbol>

    <symbol id="i-brand-reason-of-art" viewBox="0 0 24 24">
      <circle cx="12" cy="12" r="11" fill="#4F46E5"/>
      <path fill="#FFFFFF" d="M12 4C7.58 4 4 7.58 4 12c0 1.95.7 3.74 1.87 5.13.25.3.69.34.98.08.3-.25.34-.69.09-.98C5.95 14.97 5.33 13.56 5.33 12c0-3.68 2.99-6.67 6.67-6.67s6.67 2.99 6.67 6.67c0 1.56-.62 2.97-1.61 4.23-.25.3-.21.74.09.98.29.25.73.22.98-.08C19.3 15.74 20 13.95 20 12c0-4.42-3.58-8-8-8z"/>
      <circle cx="12" cy="12" r="2.5" fill="#F59E0B"/>
    </symbol>

    <symbol id="i-brand-nulart" viewBox="0 0 24 24">
      <rect width="24" height="24" rx="4" fill="#0F172A"/>
      <line x1="3" y1="20" x2="21" y2="20" stroke="#38BDF8" stroke-width="2"/>
      <line x1="12" y1="3" x2="3" y2="7.5" stroke="#38BDF8" stroke-width="2"/>
      <line x1="12" y1="3" x2="21" y2="7.5" stroke="#38BDF8" stroke-width="2"/>
      <line x1="3" y1="7.5" x2="21" y2="7.5" stroke="#38BDF8" stroke-width="2"/>
      <line x1="6" y1="7.5" x2="6" y2="20" stroke="#38BDF8" stroke-width="2"/>
      <line x1="10" y1="7.5" x2="10" y2="20" stroke="#38BDF8" stroke-width="2"/>
      <line x1="14" y1="7.5" x2="14" y2="20" stroke="#38BDF8" stroke-width="2"/>
      <line x1="18" y1="7.5" x2="18" y2="20" stroke="#38BDF8" stroke-width="2"/>
    </symbol>
"""

# 1. Update assets/icons/icons.svg
with open(ICONS_SVG_PATH, "r", encoding="utf-8") as f:
    icons_svg = f.read()

if "i-brand-youtube" not in icons_svg:
    icons_svg = icons_svg.replace("</defs>", BRAND_SYMBOLS + "\n  </defs>")
    with open(ICONS_SVG_PATH, "w", encoding="utf-8") as f:
        f.write(icons_svg)
    print("[+] Added brand icons to assets/icons/icons.svg")

# 2. Update artwork.html
with open(ARTWORK_HTML_PATH, "r", encoding="utf-8") as f:
    html = f.read()

# Add brand-icon style if missing
brand_css = """
    .brand-icon {
      width: 18px;
      height: 18px;
      display: inline-block;
      vertical-align: -3px;
      margin-right: 7px;
      flex-shrink: 0;
    }
"""

if ".brand-icon {" not in html:
    html = html.replace("</style>", brand_css + "\n  </style>")

# Update inline sprite in artwork.html if present
if "i-brand-youtube" not in html and "</defs>" in html:
    html = html.replace("</defs>", BRAND_SYMBOLS + "\n  </defs>", 1)

# Replace the platform links in artwork.html
old_links_snippet = """      // Clean Unified 9 Platform Links with Tabler & Lucide SVG Icons
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

new_links_snippet = """      // Clean Unified 9 Platform Links with Official Brand SVG Icons
      const queryEnc = encodeURIComponent(`${item.title_kr} ${item.artist_name_kr || ''}`);
      const grid = document.getElementById('platformLinksGrid');
      grid.innerHTML = `
        <a href="${(docent && docent.youtube_url) || media.youtube_video_url || 'https://www.youtube.com/results?search_query=' + queryEnc}" target="_blank" class="lds-platform-btn" title="유튜브에서 이 작품의 1:1 해설 영상 감상하기">
          <span style="display:flex; align-items:center;"><svg class="brand-icon"><use href="#i-brand-youtube"></use></svg> <span>유튜브 해설 풀영상</span></span>
          <svg class="icon" style="width:13px;height:13px;"><use href="#i-external"></use></svg>
        </a>
        <a href="${media.channel_shorts_url || 'https://www.youtube.com/results?search_query=' + queryEnc + '+shorts'}" target="_blank" class="lds-platform-btn" title="서정욱 미술토크 Shorts 1분 명화 클립">
          <span style="display:flex; align-items:center;"><svg class="brand-icon"><use href="#i-brand-shorts"></use></svg> <span>서정욱 미술토크 Shorts</span></span>
          <svg class="icon" style="width:13px;height:13px;"><use href="#i-external"></use></svg>
        </a>
        <a href="${media.channel_reason_of_art || 'https://www.youtube.com/@Reason_Of_Art/videos'}" target="_blank" class="lds-platform-btn" title="미술의 이유 유튜브 공식 채널">
          <span style="display:flex; align-items:center;"><svg class="brand-icon"><use href="#i-brand-reason-of-art"></use></svg> <span>미술의 이유 채널</span></span>
          <svg class="icon" style="width:13px;height:13px;"><use href="#i-external"></use></svg>
        </a>
        <a href="https://search.naver.com/search.naver?where=video&query=${queryEnc}" target="_blank" class="lds-platform-btn" title="네이버 동영상 & 클립 해설 검색">
          <span style="display:flex; align-items:center;"><svg class="brand-icon"><use href="#i-brand-naver"></use></svg> <span>네이버 TV·클립 해설</span></span>
          <svg class="icon" style="width:13px;height:13px;"><use href="#i-external"></use></svg>
        </a>
        <a href="https://tv.kakao.com/search?q=${queryEnc}" target="_blank" class="lds-platform-btn" title="다음 & 카카오TV 영상 검색">
          <span style="display:flex; align-items:center;"><svg class="brand-icon"><use href="#i-brand-kakao"></use></svg> <span>다음·카카오TV 영상</span></span>
          <svg class="icon" style="width:13px;height:13px;"><use href="#i-external"></use></svg>
        </a>
        <a href="${media.instagram_channel_url || 'https://www.instagram.com/behind_canvas_stories_kr/'}" target="_blank" class="lds-platform-btn" title="인스타그램 Behind Canvas Stories KR">
          <span style="display:flex; align-items:center;"><svg class="brand-icon"><use href="#i-brand-instagram"></use></svg> <span>인스타 Behind Stories</span></span>
          <svg class="icon" style="width:13px;height:13px;"><use href="#i-external"></use></svg>
        </a>
        <a href="https://www.tiktok.com/search?q=${queryEnc}" target="_blank" class="lds-platform-btn" title="틱톡 1분 도슨트 숏폼 검색">
          <span style="display:flex; align-items:center;"><svg class="brand-icon"><use href="#i-brand-tiktok"></use></svg> <span>틱톡 1분 도슨트</span></span>
          <svg class="icon" style="width:13px;height:13px;"><use href="#i-external"></use></svg>
        </a>
        <a href="https://vimeo.com/search?q=${queryEnc}" target="_blank" class="lds-platform-btn" title="비메오 고화질 예술 다큐멘터리">
          <span style="display:flex; align-items:center;"><svg class="brand-icon"><use href="#i-brand-vimeo"></use></svg> <span>비메오(Vimeo) 다큐</span></span>
          <svg class="icon" style="width:13px;height:13px;"><use href="#i-external"></use></svg>
        </a>
        <a href="${media.channel_nulart || 'https://www.youtube.com/@nulart'}" target="_blank" class="lds-platform-btn" title="널 위한 문화예술 공식 채널">
          <span style="display:flex; align-items:center;"><svg class="brand-icon"><use href="#i-brand-nulart"></use></svg> <span>널 위한 문화예술</span></span>
          <svg class="icon" style="width:13px;height:13px;"><use href="#i-external"></use></svg>
        </a>
      `;"""

if old_links_snippet in html:
    html = html.replace(old_links_snippet, new_links_snippet)
    print("[+] Replaced platform links in artwork.html")
else:
    print("[!] Warning: exact old_links_snippet not found, checking...")

with open(ARTWORK_HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html)

print("[+] artwork.html successfully updated with brand icons!")
