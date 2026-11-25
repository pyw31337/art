#!/usr/bin/env python3
import re

with open('artwork.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the start of <script>
script_pos = content.find('<script>')
if script_pos == -1:
    print("Could not find <script>")
    exit(1)

html_part = content[:script_pos]

clean_script = '''<script>
    let currentArtwork = null;
    let artworkCatalog = [];
    let currentCatalogIndex = 0;
    let wakeLock = null;
    let lowerThirdVisible = true;
    let presLowerThirdVisible = true;
    let isAutoTour = true;

    // Slideshow Auto-Advance State (OFF, 10s, 15s, 20s)
    let slideshowIntervalSeconds = 0;
    let slideshowTimer = null;
    let slideshowStartTime = 0;
    let progressAnimFrame = null;

    // Interactive Zoom & Pan State (Rock-solid 60fps Pointer-based)
    let zoomScale = 1.0;
    let panX = 0;
    let panY = 0;
    let isPointerDragging = false;
    let dragStartScreenX = 0, dragStartScreenY = 0;
    let dragStartPanX = 0, dragStartPanY = 0;
    const activePointers = new Map();
    let initialPinchDistance = 0;
    let initialPinchScale = 1.0;

    // Navigation arrows auto-hide on hover/touch
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

    ['mousemove', 'touchstart', 'click', 'pointerdown'].forEach(evt => {
      window.addEventListener(evt, triggerNavActivity, { passive: true });
    });

    // Extract artwork ID from URL (?id=...)
    const urlParams = new URLSearchParams(window.location.search);
    let targetId = urlParams.get('id') || 'sculpt_rodin_thinker';
    const autoPresentation = urlParams.get('mode') === 'presentation';

    const STORY_MAP = {
      family: { label: '가족 이야기', headline: '가족의 사랑과 따스한 유대감' },
      lovers: { label: '연인 & 애인', headline: '열정과 낭만, 사랑의 속삭임' },
      children: { label: '아이 & 동심', headline: '순수한 동심과 천진난만한 시절' },
      friendship: { label: '우정 & 연대', headline: '함께하는 이들과의 깊은 우정과 신뢰' },
      tragedy: { label: '비극 & 상실', headline: '인간의 고뇌와 슬픔, 실존적 비극' },
      solitude: { label: '자아 & 고독', headline: '내면의 성찰과 침묵 속의 사색' },
      nature: { label: '자연 & 정글', headline: '야생의 숨결과 경이로운 대자연' },
      mystery: { label: '미스터리 & 비밀', headline: '캔버스 밑에 감춰진 비밀과 미스터리' }
    };

    let videoDocentRegistry = {};

    function stripEmoji(str) {
      if (!str) return '';
      return String(str).replace(/[\\u{1F300}-\\u{1F9FF}\\u{2600}-\\u{27BF}\\u{1FA00}-\\u{1FAFF}]/gu, '').replace(/^\\s*[·•\\-]\\s*/, '').trim();
    }

    // Safe DOM text/HTML setters
    const setTxt = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val != null ? val : ''; };
    const setHtml = (id, val) => { const el = document.getElementById(id); if (el) el.innerHTML = val != null ? val : ''; };

    async function loadArtworkData() {
      try {
        try {
          videoDocentRegistry = await fetch('data/artwork_video_docent_registry.json?v=' + Date.now()).then(r => r.json());
        } catch(e) {
          console.warn("Docent registry load error:", e);
        }

        const [res1, exp, cont, resDg] = await Promise.all([
          fetch('data/art_paintings_master_db.json?v=' + Date.now()).then(r => r.json()).catch(() => ({})),
          fetch('data/expanded_art_categories_db.json?v=' + Date.now()).then(r => r.json()).catch(() => ({})),
          fetch('data/contemporary_art_and_architecture_db.json?v=' + Date.now()).then(r => r.json()).catch(() => ({})),
          fetch('data/digital_gallery_master_db.json?v=' + Date.now()).then(r => r.json()).catch(() => ({}))
        ]);

        const list1 = [...(res1.featured_masterpieces || []), ...(res1.featured_paintings || [])];
        const expList = [];
        Object.values(exp).forEach(v => {
          if (Array.isArray(v) && v.length && typeof v[0] === 'object') expList.push(...v);
        });
        const contList = [];
        Object.values(cont).forEach(v => {
          if (Array.isArray(v) && v.length && typeof v[0] === 'object') contList.push(...v);
        });
        const dgList = resDg.artworks || [];

        // Build deduplicated unified catalog
        const combined = [];
        const seenIds = new Set();
        [...list1, ...expList, ...contList, ...dgList].forEach(item => {
          const cid = item.id || item.work_id;
          if (cid && !seenIds.has(cid)) {
            seenIds.add(cid);
            combined.push(item);
          }
        });
        artworkCatalog = combined;

        // Find initial artwork
        let found = artworkCatalog.find(a => (a.id === targetId || a.work_id === targetId));
        if (!found && artworkCatalog.length > 0) {
          found = artworkCatalog[0];
        }

        if (found) {
          currentCatalogIndex = artworkCatalog.findIndex(a => (a.id === found.id || a.work_id === found.work_id));
          if (currentCatalogIndex < 0) currentCatalogIndex = 0;
          switchArtwork(found, false);
          if (autoPresentation) {
            enterPresentationMode();
          }
        }
      } catch (err) {
        console.error("Failed to load artwork data:", err);
      }
    }

    function switchArtwork(item, updateHistory = true) {
      currentArtwork = item;
      targetId = item.id || item.work_id;

      // Attach 1:1 verified docent
      const regDocent = videoDocentRegistry[item.id] || videoDocentRegistry[item.work_id];
      if (regDocent) {
        item.verified_docent = regDocent;
      }

      renderArtworkDetails(item);

      if (updateHistory) {
        const url = new URL(window.location);
        url.searchParams.set('id', targetId);
        window.history.pushState({ id: targetId }, '', url);
      }

      // Reset slideshow timer if active
      if (slideshowIntervalSeconds > 0) {
        restartSlideshowTimer();
      }
    }

    function navigateArtwork(delta) {
      if (!artworkCatalog.length) return;
      currentCatalogIndex = (currentCatalogIndex + delta + artworkCatalog.length) % artworkCatalog.length;
      const nextItem = artworkCatalog[currentCatalogIndex];
      switchArtwork(nextItem, true);

      // Smooth Ken Burns tour restart in presentation mode
      if (document.getElementById('presOverlay').classList.contains('active')) {
        resetZoomPan();
      }
    }

    function renderArtworkDetails(item) {
      document.title = `${item.title_kr} (${item.artist_name_kr || '명화'}) — 렛츠아트`;

      const imgUrl = (item.image_url || item.thumbnail_url || '').replace(/ /g, '%20');
      const fallbackSvg = "data:image/svg+xml;charset=UTF-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22600%22%20height%3D%22400%22%3E%3Crect%20width%3D%22100%25%22%20height%3D%22100%25%22%20fill%3D%22%23080a0f%22%2F%3E%3Ctext%20x%3D%2250%25%22%20y%3D%2250%25%22%20fill%3D%22%2394a3b8%22%20font-size%3D%2220%22%20text-anchor%3D%22middle%22%20dominant-baseline%3D%22middle%22%3E%EC%9E%91%ED%92%88%20%EC%A0%84%EC%8B%9C%20%EC%A4%80%EB%B9%84%20%EC%A4%91%3C%2Ftext%3E%3C%2Fsvg%3E";

      // 1. Hero Zone with multi-stage fallback
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
      };

      const heroBg = document.getElementById('heroAmbientBg');
      if (heroBg) heroBg.style.backgroundImage = `url('${imgUrl}')`;

      // De-duplicate Korean and English titles/artists
      const titleKr = (item.title_kr || '').trim();
      const titleEn = (item.title_en || '').trim();
      const cleanTitleEn = (titleEn && titleEn.toLowerCase() !== titleKr.toLowerCase()) ? titleEn : '';

      const artistKr = (item.artist_name_kr || item.architect_kr || item.author_kr || '작가 미상').trim();
      const artistEn = (item.artist_name_en || item.architect_en || item.author_en || '').trim();
      const cleanArtistEn = (artistEn && artistEn.toLowerCase() !== artistKr.toLowerCase()) ? artistEn : '';

      // Hero Lower-Third Caption
      const storyMeta = STORY_MAP[item.story_category] || STORY_MAP.solitude;
      setTxt('ltMuseumBadge', item.museum || item.location || '소장처 참조');
      setTxt('ltYearMeta', item.year ? `${item.year}년` : '연도 미상');
      setTxt('ltStoryBadge', stripEmoji(item.story_label) || storyMeta.label);
      setTxt('ltTitle', `${titleKr} ${cleanTitleEn ? `(${cleanTitleEn})` : ''}`.trim());
      setTxt('ltArtist', `${artistKr} ${cleanArtistEn ? `(${cleanArtistEn})` : ''}`.trim());
      setTxt('ltDesc', item.description || item.curator_notes || '인류의 위대한 문화유산을 감상해보세요.');

      // 2. Parallax Sheet Content
      setTxt('sheetBreadcrumb', `인류 문화유산 아카이브 / ${item.category_kr || '회화'} / ${item.movement || '명화'}`);
      setTxt('sheetTitleKr', titleKr);
      setTxt('sheetTitleEn', cleanTitleEn);
      setTxt('sheetArtistKr', artistKr);
      setTxt('sheetArtistEn', cleanArtistEn ? `(${cleanArtistEn})` : '');

      setTxt('specYear', item.year ? `${item.year}년` : '연도 미상');
      setTxt('specMedium', item.medium || '캔버스에 유채 (Oil on canvas)');
      setTxt('specDimensions', item.dimensions || '소장처 규격 정보 참조');
      setTxt('specMuseum', item.museum || item.location || '소장처 정보 참조');
      setTxt('specUrn', item.urn || `urn:art:work:${item.id || item.work_id}`);

      // Behind Story Investigation (Handmaker / Secrets)
      const secretCard = document.getElementById('behindSecretCard');
      if (item.behind_story && secretCard) {
        secretCard.style.display = 'block';
        setTxt('behindSecretContent', stripEmoji(item.behind_story));
        if (item.behind_story_source) {
          setTxt('behindSecretSource', `조사 출처: ${item.behind_story_source}`);
        }
      } else if (secretCard) {
        secretCard.style.display = 'none';
      }

      // Story Taxonomy Card
      setTxt('storyTag', `HUMAN STORY TAXONOMY · ${stripEmoji(item.story_label) || storyMeta.label}`);
      setTxt('storyHeaderTitle', storyMeta.headline);
      setTxt('storyDescription', `${titleKr} 작품은 [${item.story_label || storyMeta.label}] 테마로 분류되어 깊은 예술적 통찰과 인간적 공감을 전합니다. ${item.description || ''}`);

      // Curatorial Commentary
      setTxt('curatorCommentary', item.curator_notes || item.description || '이 작품은 시대를 뛰어넘는 조형미와 깊은 철학적 함의를 지니고 있습니다.');

      // Historical Background
      const histSec = document.getElementById('historicalSection');
      if (item.historical_background && histSec) {
        histSec.style.display = 'block';
        setTxt('historicalContent', item.historical_background);
      } else if (histSec) {
        histSec.style.display = 'none';
      }

      // Minimalist Palette Swatches
      const paletteContainer = document.getElementById('paletteSwatches');
      if (paletteContainer) {
        if (item.palette && item.palette.length) {
          paletteContainer.innerHTML = item.palette.map(hex => `
            <div class="palette-item" onclick="navigator.clipboard.writeText('${hex}'); alert('색상코드 ${hex} 복사되었습니다.');" title="클릭하여 복사">
              <div class="palette-color" style="background:${hex};"></div>
              <span class="palette-hex">${hex}</span>
            </div>
          `).join('');
        } else {
          paletteContainer.innerHTML = '<span class="lds-mono" style="font-size:11px; color:var(--lds-text-muted);">PALETTE DATA PENDING</span>';
        }
      }

      // 3. Multimedia Docent Hub (1:1 Exact Artwork Match & Clean De-duplicated Dock)
      const media = item.media_resources || {};
      const docent = item.verified_docent || (videoDocentRegistry ? (videoDocentRegistry[item.id] || videoDocentRegistry[item.work_id]) : null);
      const docentIframe = document.getElementById('docentYoutubeIframe');
      const docentTitle = document.getElementById('docentVideoTitle');
      const analysisBox = document.getElementById('docentAnalysisBox');

      const videoId = (docent && docent.video_id) || media.youtube_video_id || "sdQQjbPqbm4";
      if (docentIframe) {
        docentIframe.src = `https://www.youtube-nocookie.com/embed/${videoId}`;
      }
      
      if (docent) {
        let cleanTitle = docent.video_title || '';
        if (docent.channel_name && cleanTitle.includes(docent.channel_name)) {
          cleanTitle = cleanTitle.replace(`[${docent.channel_name}]`, '').replace(docent.channel_name, '').trim();
        }
        cleanTitle = cleanTitle.replace(/^[\\[\\(]?[^\\]\\)]*[\\]\\)]?\\s*[:\\-]?\\s*/, '').trim() || docent.video_title;
        setHtml('docentVideoTitle', `<span class="docent-cinema-channel-tag">[${docent.channel_name}]</span> ${cleanTitle}`);
        
        if (analysisBox) {
          analysisBox.style.display = 'block';
          setTxt('docentAnalysisChannel', `${docent.channel_name} · 1:1 작품 전용 해설`);
          setTxt('docentAnalysisDuration', `영상 러닝타임 ${docent.duration || '약 15분'}`);
          setTxt('docentAnalysisSummary', docent.review_summary || '');
          setHtml('docentCuratorQuote', `<strong>큐레이터 시선:</strong> ${docent.curator_takeaway || ''}`);
        }
      } else {
        setTxt('docentVideoTitle', media.youtube_title || `${artistKr} 명화 해설`);
        if (analysisBox) analysisBox.style.display = 'none';
      }

      // Clean De-duplicated 9 Platform Dock Grid
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
      }

      // 4. Setup Presentation Mode Data
      const presImg = document.getElementById('presImg');
      if (presImg) {
        presImg.src = imgUrl;
        presImg.onerror = () => { presImg.src = fallbackSvg; };
      }
      setTxt('presStoryBadge', stripEmoji(item.story_label) || storyMeta.label);
      setTxt('presMuseumBadge', item.museum || item.location || '소장처 참조');
      setTxt('presTitle', titleKr);
      setTxt('presArtist', `${artistKr} ${item.year ? `(${item.year})` : ''}`);
      setTxt('presDesc', item.curator_notes || item.description || '');
    }

    // Toggle Lower-Third (Icon-Only Clean Design)
    function toggleLowerThird() {
      const el = document.getElementById('heroLowerThird');
      const icon = document.getElementById('toggleSubtitleIcon');
      lowerThirdVisible = !lowerThirdVisible;
      if (lowerThirdVisible) {
        el.classList.remove('hidden');
        if (icon) icon.innerHTML = '<svg class="icon"><use href="#i-message"></use></svg>';
      } else {
        el.classList.add('hidden');
        if (icon) icon.innerHTML = '<svg class="icon"><use href="#i-eye-off"></use></svg>';
      }
    }

    function scrollToSheet() {
      document.getElementById('contentSheet').scrollIntoView({ behavior: 'smooth' });
    }

    function scrollToDocent() {
      document.getElementById('docentHubSection').scrollIntoView({ behavior: 'smooth' });
    }

    // ========================================================
    // SLIDESHOW INTERVAL TIMER (OFF / 10s / 15s / 20s)
    // ========================================================
    function cycleSlideshowInterval() {
      const intervals = [0, 10, 15, 20];
      const curIdx = intervals.indexOf(slideshowIntervalSeconds);
      const nextIdx = (curIdx + 1) % intervals.length;
      slideshowIntervalSeconds = intervals[nextIdx];

      const badge = document.getElementById('intervalBadge');
      if (slideshowIntervalSeconds === 0) {
        if (badge) badge.textContent = 'OFF';
        clearSlideshowTimer();
      } else {
        if (badge) badge.textContent = `${slideshowIntervalSeconds}s`;
        restartSlideshowTimer();
      }
    }

    function clearSlideshowTimer() {
      if (slideshowTimer) clearInterval(slideshowTimer);
      slideshowTimer = null;
      if (progressAnimFrame) cancelAnimationFrame(progressAnimFrame);
      progressAnimFrame = null;
      const bar = document.getElementById('slideshowProgressBar');
      if (bar) bar.style.width = '0%';
    }

    function restartSlideshowTimer() {
      clearSlideshowTimer();
      if (slideshowIntervalSeconds <= 0) return;

      slideshowStartTime = performance.now();
      const durationMs = slideshowIntervalSeconds * 1000;
      const bar = document.getElementById('slideshowProgressBar');

      function updateProgress() {
        const elapsed = performance.now() - slideshowStartTime;
        const progress = Math.min(100, (elapsed / durationMs) * 100);
        if (bar) bar.style.width = `${progress}%`;

        if (elapsed < durationMs) {
          progressAnimFrame = requestAnimationFrame(updateProgress);
        } else {
          if (bar) bar.style.width = '100%';
          navigateArtwork(1);
        }
      }
      progressAnimFrame = requestAnimationFrame(updateProgress);
    }

    // ========================================================
    // AI VOICE DOCENT ENGINE
    // ========================================================
    let voiceSynth = window.speechSynthesis;
    let voiceUtterance = null;
    let isVoicePlaying = false;
    let currentVoiceRate = 1.0;

    function getCuratedDocentScript() {
      if (!currentArtwork) return "";
      const title = currentArtwork.title_kr || currentArtwork.title || "명화";
      const artist = currentArtwork.artist_name_kr || currentArtwork.artist || "작가 미상";
      const year = currentArtwork.year || "연도 미상";
      const museum = currentArtwork.museum || currentArtwork.location || "소장처";
      const behind = currentArtwork.behind_story ? ` 비하인드 조사 기록에 따르면, ${currentArtwork.behind_story}` : '';
      const notes = currentArtwork.curator_notes || currentArtwork.description || "";

      return `안녕하세요. 렛츠아트 인공지능 음성 도슨트입니다. `
        + `지금 감상하시는 작품은 ${artist}의 걸작, ${title}입니다. `
        + `${year}년에 완성되었으며, 현재 ${museum}에 소장되어 있습니다. `
        + `${notes} `
        + `${behind} `
        + `화면을 통해 명화의 붓터치와 빛의 울림을 천천히 감상해보시기 바랍니다.`;
    }

    function toggleVoiceDocent() {
      if (!('speechSynthesis' in window)) {
        alert("현재 브라우저 환경에서 음성 합성을 지원하지 않습니다.");
        return;
      }

      if (isVoicePlaying) {
        window.speechSynthesis.cancel();
        isVoicePlaying = false;
        updateVoiceUI(false);
      } else {
        window.speechSynthesis.cancel();
        const script = getCuratedDocentScript();
        if (!script) return;

        voiceUtterance = new SpeechSynthesisUtterance(script);
        voiceUtterance.rate = currentVoiceRate;
        voiceUtterance.pitch = 1.0;
        voiceUtterance.lang = 'ko-KR';

        const voices = window.speechSynthesis.getVoices();
        const koVoice = voices.find(v => v.lang === 'ko-KR' || v.lang.startsWith('ko'));
        if (koVoice) voiceUtterance.voice = koVoice;

        voiceUtterance.onstart = () => { isVoicePlaying = true; updateVoiceUI(true); };
        voiceUtterance.onend = () => { isVoicePlaying = false; updateVoiceUI(false); };
        voiceUtterance.onerror = () => { isVoicePlaying = false; updateVoiceUI(false); };

        window.speechSynthesis.speak(voiceUtterance);
      }
    }

    function setVoiceRate(rate) {
      currentVoiceRate = rate;
      document.querySelectorAll('.voice-rate-btn').forEach(b => {
        b.classList.toggle('active', parseFloat(b.dataset.rate) === rate);
      });
      if (isVoicePlaying) {
        toggleVoiceDocent();
        setTimeout(toggleVoiceDocent, 150);
      }
    }

    function updateVoiceUI(playing) {
      const navText = document.getElementById('voiceNavText');
      const sheetBtnText = document.getElementById('sheetVoiceBtnText');
      const soundwave = document.getElementById('voiceSoundwave');
      const statusLabel = document.getElementById('voiceStatusLabel');
      const playIcon = document.getElementById('voicePlayIcon');

      if (playing) {
        if (navText) navText.textContent = "해설 멈춤";
        if (sheetBtnText) sheetBtnText.textContent = "AI 해설 멈춤";
        if (soundwave) soundwave.classList.add('active');
        if (playIcon) playIcon.innerHTML = '<svg class="icon"><use href="#i-pause"></use></svg>';
        if (statusLabel) statusLabel.textContent = "AI 음성 도슨트가 명화의 역사와 도상학적 비하인드 스토리를 해설 중입니다";
      } else {
        if (navText) navText.textContent = "음성 도슨트";
        if (sheetBtnText) sheetBtnText.textContent = "AI 한국어 음성 도슨트 해설 재생";
        if (soundwave) soundwave.classList.remove('active');
        if (playIcon) playIcon.innerHTML = '<svg class="icon"><use href="#i-mic"></use></svg>';
        if (statusLabel) statusLabel.textContent = "명화의 역사와 도상학적 비하인드 스토리를 음성으로 안내합니다";
      }
    }

    // ========================================================
    // PRESENTATION GALLERY (디지털 액자 & WAKELOCK)
    // ========================================================
    async function enterPresentationMode() {
      const overlay = document.getElementById('presOverlay');
      overlay.classList.add('active');

      try {
        if (document.documentElement.requestFullscreen) {
          await document.documentElement.requestFullscreen();
        } else if (document.documentElement.webkitRequestFullscreen) {
          await document.documentElement.webkitRequestFullscreen();
        }
      } catch (e) {
        console.warn("Fullscreen request notice:", e);
      }

      requestScreenWakeLock();
      resetZoomPan();
    }

    async function exitPresentationMode() {
      const overlay = document.getElementById('presOverlay');
      overlay.classList.remove('active');

      releaseScreenWakeLock();
      clearSlideshowTimer();

      try {
        if (document.fullscreenElement) {
          await document.exitFullscreen();
        } else if (document.webkitFullscreenElement) {
          await document.webkitExitFullscreen();
        }
      } catch (e) {}
    }

    async function requestScreenWakeLock() {
      const dot = document.getElementById('wakeLockDot');
      if ('wakeLock' in navigator) {
        try {
          wakeLock = await navigator.wakeLock.request('screen');
          if (dot) {
            dot.style.background = '#10b981';
            dot.style.boxShadow = '0 0 10px #10b981';
            dot.title = '화면 꺼짐 방지 활성화 (WakeLock)';
          }
          wakeLock.addEventListener('release', () => {
            if (dot) {
              dot.style.background = '#64748b';
              dot.style.boxShadow = 'none';
              dot.title = '화면 꺼짐 방지 해제됨';
            }
          });
        } catch (err) {
          if (dot) dot.style.display = 'none';
        }
      } else {
        if (dot) dot.style.display = 'none';
      }
    }

    function releaseScreenWakeLock() {
      if (wakeLock) {
        wakeLock.release().then(() => { wakeLock = null; });
      }
    }

    function toggleAutoTour() {
      setAutoTour(!isAutoTour);
    }

    function setAutoTour(active) {
      isAutoTour = active;
      const img = document.getElementById('presImg');
      const btn = document.getElementById('btnTourToggle');
      if (isAutoTour) {
        if (img) img.classList.add('auto-tour');
        if (btn) btn.classList.add('active');
        resetZoomPan();
      } else {
        if (img) img.classList.remove('auto-tour');
        if (btn) btn.classList.remove('active');
      }
    }

    function togglePresSubtitle() {
      presLowerThirdVisible = !presLowerThirdVisible;
      const lt = document.getElementById('presLowerThird');
      if (presLowerThirdVisible) {
        lt.classList.remove('hidden');
      } else {
        lt.classList.add('hidden');
      }
    }

    // ========================================================
    // 60FPS ROCK-SOLID POINTER-BASED DRAG & ZOOM ENGINE
    // ========================================================
    function applyPresTransform() {
      const img = document.getElementById('presImg');
      if (!img) return;

      // When zooming or panning, cancel CSS keyframe camera tour immediately
      if (isAutoTour) {
        setAutoTour(false);
      }

      // translate3d first, scale second: ensures 1:1 screen pixel dragging!
      img.style.transform = `translate3d(${panX}px, ${panY}px, 0) scale(${zoomScale})`;
    }

    function zoomIn() {
      zoomScale = Math.min(zoomScale * 1.25, 6.0);
      const img = document.getElementById('presImg');
      if (img) img.style.transition = 'transform 0.15s cubic-bezier(0.2, 0, 0, 1)';
      applyPresTransform();
    }

    function zoomOut() {
      zoomScale = Math.max(zoomScale * 0.8, 0.75);
      const img = document.getElementById('presImg');
      if (img) img.style.transition = 'transform 0.15s cubic-bezier(0.2, 0, 0, 1)';
      applyPresTransform();
    }

    function resetZoomPan() {
      zoomScale = 1.0;
      panX = 0;
      panY = 0;
      const img = document.getElementById('presImg');
      if (img) {
        img.style.transition = 'transform 0.25s cubic-bezier(0.2, 0, 0, 1)';
        img.style.transform = '';
      }
      if (isAutoTour) {
        img.classList.add('auto-tour');
      }
    }

    const presCanvas = document.getElementById('presCanvasWrap');
    const presImgEl = document.getElementById('presImg');

    if (presCanvas) {
      // 1. Mouse Wheel Zoom centered around pointer
      presCanvas.addEventListener('wheel', (e) => {
        e.preventDefault();
        if (isAutoTour) setAutoTour(false);

        const zoomFactor = e.deltaY < 0 ? 1.14 : 0.88;
        const newScale = Math.min(Math.max(0.7, zoomScale * zoomFactor), 6.0);

        const rect = presCanvas.getBoundingClientRect();
        const cursorX = e.clientX - rect.left - rect.width / 2;
        const cursorY = e.clientY - rect.top - rect.height / 2;

        panX = cursorX - (cursorX - panX) * (newScale / zoomScale);
        panY = cursorY - (cursorY - panY) * (newScale / zoomScale);
        zoomScale = newScale;

        if (presImgEl) presImgEl.style.transition = 'transform 0.1s ease-out';
        applyPresTransform();
      }, { passive: false });

      // 2. High-performance PointerDrag (Desktop Mouse + Mobile Touch unified)
      presCanvas.addEventListener('pointerdown', (e) => {
        activePointers.set(e.pointerId, { x: e.clientX, y: e.clientY });

        if (activePointers.size === 1) {
          isPointerDragging = true;
          dragStartScreenX = e.clientX;
          dragStartScreenY = e.clientY;
          dragStartPanX = panX;
          dragStartPanY = panY;

          if (isAutoTour) setAutoTour(false);
          presCanvas.classList.add('is-dragging');
          if (presImgEl) presImgEl.style.transition = 'none'; // Instant 60fps tracking!
          try { presCanvas.setPointerCapture(e.pointerId); } catch(err){}
        } else if (activePointers.size === 2) {
          // Pinch-to-zoom start
          const pts = Array.from(activePointers.values());
          initialPinchDistance = Math.hypot(pts[0].x - pts[1].x, pts[0].y - pts[1].y);
          initialPinchScale = zoomScale;
        }
      });

      presCanvas.addEventListener('pointermove', (e) => {
        if (!activePointers.has(e.pointerId)) return;
        activePointers.set(e.pointerId, { x: e.clientX, y: e.clientY });

        if (activePointers.size === 1 && isPointerDragging) {
          const dx = e.clientX - dragStartScreenX;
          const dy = e.clientY - dragStartScreenY;
          panX = dragStartPanX + dx;
          panY = dragStartPanY + dy;
          applyPresTransform();
        } else if (activePointers.size === 2 && initialPinchDistance > 0) {
          const pts = Array.from(activePointers.values());
          const curDist = Math.hypot(pts[0].x - pts[1].x, pts[0].y - pts[1].y);
          const ratio = curDist / initialPinchDistance;
          zoomScale = Math.min(Math.max(0.7, initialPinchScale * ratio), 6.0);
          applyPresTransform();
        }
      });

      const endPointer = (e) => {
        activePointers.delete(e.pointerId);
        if (activePointers.size === 0) {
          isPointerDragging = false;
          presCanvas.classList.remove('is-dragging');
          if (presImgEl) presImgEl.style.transition = 'transform 0.15s cubic-bezier(0.2, 0, 0, 1)';
        }
        try { presCanvas.releasePointerCapture(e.pointerId); } catch(err){}
      };

      presCanvas.addEventListener('pointerup', endPointer);
      presCanvas.addEventListener('pointercancel', endPointer);

      // Double click to toggle smart zoom (2.2x) or reset
      presCanvas.addEventListener('dblclick', () => {
        if (zoomScale > 1.1) {
          resetZoomPan();
        } else {
          zoomScale = 2.2;
          panX = 0;
          panY = 0;
          if (presImgEl) presImgEl.style.transition = 'transform 0.25s cubic-bezier(0.2, 0, 0, 1)';
          applyPresTransform();
        }
      });
    }

    // Keyboard Shortcuts: Left/Right arrows for artwork navigation, Esc to exit
    window.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowRight') {
        navigateArtwork(1);
      } else if (e.key === 'ArrowLeft') {
        navigateArtwork(-1);
      } else if (e.key === 'Escape') {
        if (document.getElementById('presOverlay').classList.contains('active')) {
          exitPresentationMode();
        }
      }
    });

    // Handle browser back/forward buttons
    window.addEventListener('popstate', (e) => {
      const curId = new URLSearchParams(window.location.search).get('id');
      if (curId && artworkCatalog.length) {
        const item = artworkCatalog.find(a => (a.id === curId || a.work_id === curId));
        if (item) switchArtwork(item, false);
      }
    });

    loadArtworkData();

    if ('serviceWorker' in navigator) {
      window.addEventListener('load', () => {
        navigator.serviceWorker.register('sw.js').catch(err => console.log('SW reg fail:', err));
      });
    }
  </script>
</body>
</html>
'''

full_code = html_part + clean_script
with open('artwork.html', 'w', encoding='utf-8') as f:
    f.write(full_code)

print("Injected clean modern script successfully.")
