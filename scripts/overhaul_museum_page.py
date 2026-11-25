import json

# Read data/top_museums_master_catalog.json
with open('data/top_museums_master_catalog.json', 'r', encoding='utf-8') as f:
    cat_data = json.load(f)

museums = cat_data.get('museums', [])

museum_html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <meta name="theme-color" content="#090d16">
  <link rel="manifest" href="manifest.webmanifest">
  <link rel="icon" type="image/png" sizes="32x32" href="assets/icons/favicon-32.png">
  <link rel="apple-touch-icon" href="assets/icons/apple-touch-icon.png">
  <link rel="stylesheet" href="https://pyw31337.github.io/lets/css/lets-design-system.css?v=1.1.0">
  <title>글로벌 10대 미술관 & 국립 박물관 테마관 — 렛츠아트 (Let's Art)</title>
  <style>
    :root {{
      --lds-brand-600: #2563eb;
      --lds-brand-700: #1d4ed8;
      --lds-canvas-bg: #ffffff;
      --lds-surface-subtle: #f8fafc;
      --lds-divider-faint: #f1f5f9;
      --lds-divider-line: #e2e8f0;
      --lds-text-strong: #0f172a;
      --lds-text-body: #334155;
      --lds-text-muted: #64748b;
      --lds-text-faint: #94a3b8;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; min-width: 0; }}
    body {{
      background: var(--lds-canvas-bg);
      color: var(--lds-text-body);
      font-family: var(--lds-font-sans);
      font-size: 13px;
      line-height: 1.5;
      -webkit-font-smoothing: antialiased;
      min-height: 100vh;
    }}

    .icon {{
      width: 16px;
      height: 16px;
      fill: none !important;
      stroke: currentColor !important;
      stroke-width: 1.8 !important;
      stroke-linecap: round !important;
      stroke-linejoin: round !important;
      display: inline-block;
      vertical-align: middle;
      flex-shrink: 0;
    }}

    /* Global Nav Header */
    .top-global-header {{
      background: #090d16;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      padding: 14px 28px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      position: sticky;
      top: 0;
      z-index: 50;
    }}
    .logo-area {{ display: flex; align-items: center; gap: 12px; }}
    .logo-badge {{
      width: 32px; height: 32px;
      border-radius: 6px;
      background: #2563eb;
      color: #ffffff;
      display: grid;
      place-items: center;
    }}
    .header-title-text {{
      font-size: 16px;
      font-weight: 800;
      color: #ffffff;
      letter-spacing: -0.3px;
    }}
    .nav-links {{ display: flex; gap: 8px; align-items: center; }}
    .lds-btn-nav {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 14px;
      border-radius: 4px;
      font-size: 12px;
      font-weight: 600;
      color: #cbd5e1;
      text-decoration: none;
      border: 1px solid rgba(255, 255, 255, 0.12);
      background: rgba(255, 255, 255, 0.05);
      transition: all 0.15s ease;
    }}
    .lds-btn-nav:hover {{ background: rgba(255, 255, 255, 0.15); color: #ffffff; }}
    .lds-btn-nav.active {{ background: #2563eb; color: #ffffff; border-color: #2563eb; }}

    /* ========================================================
       GRAND IMMERSIVE THEME PAVILION HERO ZONE
       ======================================================== */
    .museum-pavilion-hero {{
      position: relative;
      height: 480px;
      background: #090d16;
      color: #ffffff;
      overflow: hidden;
      display: flex;
      align-items: flex-end;
      padding: 48px 36px;
    }}
    .hero-bg-photo {{
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      object-fit: cover;
      filter: brightness(0.65) saturate(1.1);
      transform: scale(1.02);
      transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    .hero-vignette-overlay {{
      position: absolute;
      inset: 0;
      background: linear-gradient(0deg, rgba(9, 13, 22, 0.95) 0%, rgba(9, 13, 22, 0.45) 50%, rgba(9, 13, 22, 0.8) 100%);
      pointer-events: none;
    }}
    .hero-content-box {{
      position: relative;
      z-index: 10;
      max-width: 960px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }}
    .pavilion-badge-row {{
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }}
    .pavilion-pill {{
      font-family: var(--lds-font-mono);
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.08em;
      color: #60a5fa;
      background: rgba(37, 99, 235, 0.25);
      padding: 4px 12px;
      border-radius: 999px;
      border: 1px solid rgba(59, 130, 246, 0.4);
      text-transform: uppercase;
    }}
    .museum-hero-title {{
      font-size: 38px;
      font-weight: 900;
      color: #ffffff;
      letter-spacing: -0.8px;
      line-height: 1.15;
    }}
    .museum-hero-title-en {{
      font-size: 16px;
      color: #94a3b8;
      font-weight: 400;
      font-style: italic;
    }}
    .museum-hero-meta-row {{
      display: flex;
      align-items: center;
      gap: 16px;
      flex-wrap: wrap;
      font-size: 13px;
      color: #cbd5e1;
    }}
    .museum-hero-meta-item {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}
    .museum-hero-desc {{
      font-size: 14.5px;
      line-height: 1.7;
      color: #e2e8f0;
      max-width: 860px;
    }}

    /* Main Container */
    .container {{ max-width: 1440px; margin: 0 auto; padding: 24px 28px 80px; }}

    /* Museum Selection Horizontal Strip */
    .museum-selection-strip {{
      display: flex;
      gap: 10px;
      overflow-x: auto;
      padding: 16px 0;
      margin-bottom: 28px;
      border-bottom: 1px solid var(--lds-divider-faint);
      scrollbar-width: thin;
    }}
    .museum-selection-strip::-webkit-scrollbar {{ height: 4px; }}
    .museum-selection-strip::-webkit-scrollbar-thumb {{ background: #cbd5e1; border-radius: 2px; }}

    .museum-pill-tab {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 16px;
      background: #f8fafc;
      border: 1px solid var(--lds-divider-line);
      border-radius: 999px;
      font-size: 13px;
      font-weight: 600;
      color: var(--lds-text-strong);
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.15s ease;
      flex-shrink: 0;
      text-decoration: none;
    }}
    .museum-pill-tab:hover {{
      background: #eff6ff;
      border-color: #3b82f6;
      color: #2563eb;
    }}
    .museum-pill-tab.active {{
      background: #2563eb;
      color: #ffffff;
      border-color: #2563eb;
    }}

    /* Curator Theme Pavilion Quote Box */
    .pavilion-curator-box {{
      background: linear-gradient(135deg, #090d16 0%, #111827 100%);
      border-left: 3px solid #3b82f6;
      padding: 20px 24px;
      color: #f1f5f9;
      margin-bottom: 32px;
      font-size: 13.5px;
      line-height: 1.8;
      display: flex;
      align-items: flex-start;
      gap: 16px;
    }}

    /* Grid Section Header */
    .grid-header-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      padding-bottom: 10px;
      border-bottom: 1px solid var(--lds-divider-faint);
    }}
    .grid-header-title {{
      font-size: 18px;
      font-weight: 800;
      color: var(--lds-text-strong);
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    /* Anti-Box Flat Masterpiece Grid */
    .museum-art-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 28px 24px;
    }}
    .art-flat-card {{
      display: flex;
      flex-direction: column;
      gap: 10px;
      transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    .art-flat-card:hover {{
      transform: translateY(-2px);
    }}
    .art-flat-thumb {{
      aspect-ratio: 4/3;
      background: #0f172a;
      border-radius: 6px;
      overflow: hidden;
      position: relative;
    }}
    .art-flat-img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: transform 0.3s ease;
    }}
    .art-flat-card:hover .art-flat-img {{
      transform: scale(1.03);
    }}
    .art-flat-badge {{
      position: absolute;
      top: 10px;
      left: 10px;
      background: rgba(15, 23, 42, 0.75);
      backdrop-filter: blur(8px);
      color: #ffffff;
      font-family: var(--lds-font-mono);
      font-size: 10px;
      padding: 3px 8px;
      border-radius: 4px;
    }}
    .art-flat-info {{
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}
    .art-flat-title {{
      font-size: 14.5px;
      font-weight: 700;
      color: var(--lds-text-strong);
      text-decoration: none;
      line-height: 1.4;
    }}
    .art-flat-title:hover {{
      color: #2563eb;
    }}
    .art-flat-artist {{
      font-size: 12.5px;
      color: var(--lds-text-muted);
    }}
    .art-flat-actions {{
      display: flex;
      gap: 8px;
      margin-top: 6px;
    }}
    .art-flat-btn {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font-size: 11.5px;
      font-weight: 600;
      text-decoration: none;
      color: #2563eb;
      padding: 4px 8px;
      background: #eff6ff;
      border-radius: 4px;
      transition: all 0.15s ease;
    }}
    .art-flat-btn:hover {{ background: #dbeafe; }}
  </style>
</head>
<body>

  <!-- Top Global Header -->
  <header class="top-global-header">
    <div class="logo-area">
      <div class="logo-badge">
        <svg class="icon"><use href="#i-museum"/></svg>
      </div>
      <span class="header-title-text">렛츠아트 미술관 테마관</span>
    </div>
    <nav class="nav-links">
      <a href="index.html" class="lds-btn-nav">홈</a>
      <a href="museum.html" class="lds-btn-nav active">10대 미술관</a>
      <a href="artist.html" class="lds-btn-nav">거장 아카이브</a>
      <a href="admin" class="lds-btn-nav">관제 어드민</a>
    </nav>
  </header>

  <!-- SVG Icons Suite -->
  <svg xmlns="http://www.w3.org/2000/svg" style="display: none;">
    <defs>
      <symbol id="i-museum" viewBox="0 0 24 24">
        <line x1="3" y1="21" x2="21" y2="21"></line>
        <line x1="12" y1="3" x2="3" y2="8"></line>
        <line x1="12" y1="3" x2="21" y2="8"></line>
        <line x1="3" y1="8" x2="21" y2="8"></line>
        <line x1="6" y1="8" x2="6" y2="21"></line>
        <line x1="10" y1="8" x2="10" y2="21"></line>
        <line x1="14" y1="8" x2="14" y2="21"></line>
        <line x1="18" y1="8" x2="18" y2="21"></line>
      </symbol>
      <symbol id="i-frame" viewBox="0 0 24 24">
        <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
        <circle cx="8.5" cy="8.5" r="1.5"></circle>
        <polyline points="21 15 16 10 5 21"></polyline>
      </symbol>
      <symbol id="i-sparkles" viewBox="0 0 24 24">
        <path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z"></path>
      </symbol>
      <symbol id="i-arrow-right" viewBox="0 0 24 24">
        <line x1="5" y1="12" x2="19" y2="12"></line>
        <polyline points="12 5 19 12 12 19"></polyline>
      </symbol>
    </defs>
  </svg>

  <!-- Grand Immersive Theme Pavilion Hero Zone -->
  <section class="museum-pavilion-hero" id="pavilionHero">
    <img class="hero-bg-photo" id="heroBgPhoto" src="assets/museums/louvre.jpg" alt="Museum Pavilion">
    <div class="hero-vignette-overlay"></div>
    <div class="hero-content-box">
      <div class="pavilion-badge-row">
        <span class="pavilion-pill">GLOBAL MASTERPIECE PAVILION</span>
        <span class="pavilion-pill" id="heroCollectionBadge" style="color:#fde68a; border-color:rgba(253, 230, 138, 0.4); background:rgba(217, 119, 6, 0.2);">소장품 380,000+</span>
      </div>
      <h1 class="museum-hero-title" id="heroTitleKr">파리 루브르 박물관</h1>
      <div class="museum-hero-title-en" id="heroTitleEn">Musée du Louvre</div>
      <div class="museum-hero-meta-row">
        <span class="museum-hero-meta-item">📍 <span id="heroCity">프랑스 파리</span></span>
        <span class="museum-hero-meta-item">🏛️ <span id="heroEstablished">1793년 개관</span></span>
        <span class="museum-hero-meta-item">🌐 <span>공식 디지털 갤러리 원장 연동</span></span>
      </div>
      <p class="museum-hero-desc" id="heroDesc">
        세계에서 가장 많은 방문객이 찾는 세계 최대의 미술관. 르네상스부터 19세기까지 인류 예술사의 기적이라 불리는 소장품을 품고 있으며, <모나리자>, <사모트라케의 니케>, <밀로의 비너스>가 자리한 프랑스 문화의 상징입니다.
      </p>
    </div>
  </section>

  <div class="container">
    <!-- Museum Selection Strip -->
    <div class="museum-selection-strip" id="museumSelectionStrip"></div>

    <!-- Curator Theme Pavilion Insight -->
    <div class="pavilion-curator-box">
      <svg class="icon" style="color:#60a5fa; width:22px; height:22px; margin-top:2px;"><use href="#i-sparkles"/></svg>
      <div>
        <div style="font-weight:700; color:#60a5fa; margin-bottom:4px; font-size:12px; letter-spacing:0.05em;">CURATORIAL PAVILION PERSPECTIVE</div>
        <div id="curatorPavilionText">미술관 큐레이터 관점 로딩 중...</div>
      </div>
    </div>

    <!-- Grid Header -->
    <div class="grid-header-row">
      <div class="grid-header-title">
        <svg class="icon" style="color:#2563eb;"><use href="#i-frame"/></svg>
        <span id="museumGridTitle">테마관 소장 및 대표 걸작</span>
      </div>
      <span style="font-family:var(--lds-font-mono); font-size:12px; color:var(--lds-text-muted);" id="museumWorkCount">0 ITEMS</span>
    </div>

    <!-- Artworks Flat Grid -->
    <div class="museum-art-grid" id="museumArtGrid"></div>
  </div>

  <script>
    let MUSEUMS = {json.dumps(museums, ensure_ascii=False, indent=4)};
    let allArtworks = [];
    let currentMuseumId = "louvre";

    // Read URL query parameter ?id=...
    const urlParams = new URLSearchParams(window.location.search);
    const targetMuseumParam = urlParams.get('id');
    if (targetMuseumParam && MUSEUMS.some(m => m.id === targetMuseumParam)) {{
      currentMuseumId = targetMuseumParam;
    }}

    async function initMuseumPavilion() {{
      // 1. Render Strip
      const strip = document.getElementById('museumSelectionStrip');
      strip.innerHTML = MUSEUMS.map(m => `
        <button class="museum-pill-tab ${{m.id === currentMuseumId ? 'active' : ''}}" onclick="selectMuseum('${{m.id}}')" id="tab-${{m.id}}">
          <svg class="icon"><use href="#i-museum"/></svg>
          <span>${{m.name_kr}}</span>
        </button>
      `).join('');

      // 2. Fetch all collections (7,865+ works)
      try {{
        const [rPaint, rDg, rExp, rCont] = await Promise.all([
          fetch('data/art_paintings_master_db.json?v=' + Date.now()).then(r => r.json()).catch(() => ({{ featured_masterpieces: [] }})),
          fetch('data/digital_gallery_master_db.json?v=' + Date.now()).then(r => r.json()).catch(() => ({{ artworks: [] }})),
          fetch('data/expanded_art_categories_db.json?v=' + Date.now()).then(r => r.json()).catch(() => ({{}})),
          fetch('data/contemporary_art_and_architecture_db.json?v=' + Date.now()).then(r => r.json()).catch(() => ({{}}))
        ]);

        const combined = [...(rPaint.featured_masterpieces || []), ...(rPaint.featured_paintings || []), ...(rDg.artworks || [])];
        Object.values(rExp).forEach(v => {{
          if (Array.isArray(v) && v.length && typeof v[0] === 'object') combined.push(...v);
        }});
        Object.values(rCont).forEach(v => {{
          if (Array.isArray(v) && v.length && typeof v[0] === 'object') combined.push(...v);
        }});

        // Deduplicate
        const seen = new Set();
        allArtworks = [];
        combined.forEach(it => {{
          const cid = it.id || it.work_id;
          if (cid && !seen.has(cid)) {{
            seen.add(cid);
            allArtworks.push(it);
          }}
        }});

        selectMuseum(currentMuseumId, false);
      }} catch (err) {{
        console.error("Museum collection fetch error:", err);
      }}
    }}

    function selectMuseum(id, updateHistory = true) {{
      currentMuseumId = id;
      document.querySelectorAll('.museum-pill-tab').forEach(t => {{
        t.classList.toggle('active', t.id === `tab-${{id}}`);
      }});

      const m = MUSEUMS.find(x => x.id === id);
      if (!m) return;

      // Update Immersive Theme Pavilion Hero Zone
      document.getElementById('heroBgPhoto').src = m.image;
      document.getElementById('heroTitleKr').textContent = m.name_kr;
      document.getElementById('heroTitleEn').textContent = m.name_en;
      document.getElementById('heroCity').textContent = m.city;
      document.getElementById('heroEstablished').textContent = `${{m.established}} 개관`;
      document.getElementById('heroDesc').textContent = m.description;
      document.getElementById('heroCollectionBadge').textContent = `원장 소장품 ${{m.collection_count_display}}`;
      document.getElementById('curatorPavilionText').textContent = m.curator_note;

      if (updateHistory) {{
        const url = new URL(window.location);
        url.searchParams.set('id', id);
        window.history.pushState({{ id }}, '', url);
      }}

      // Match artworks by direct museum string OR key artists
      const mArtists = (m.artists || []).map(a => a.toLowerCase().trim());
      const matched = allArtworks.filter(art => {{
        const mus = (art.museum || art.location || art.museum_key || '').toLowerCase();
        const akr = (art.artist_name_kr || art.artist || '').toLowerCase();
        const aen = (art.artist_name_en || '').toLowerCase();

        // 1. Direct museum match
        if (id === 'louvre' && (mus.includes('루브르') || mus.includes('louvre'))) return true;
        if (id === 'moma' && (mus.includes('moma') || mus.includes('근대미술관'))) return true;
        if (id === 'met' && (mus.includes('메트로폴리탄') || mus.includes('metropolitan') || mus.includes('the met'))) return true;
        if (id === 'orsay' && (mus.includes('오르세') || mus.includes('orsay'))) return true;
        if (id === 'prado' && (mus.includes('프라도') || mus.includes('prado'))) return true;
        if (id === 'uffizi' && (mus.includes('우피치') || mus.includes('uffizi'))) return true;
        if (id === 'national_gallery' && (mus.includes('내셔널') || mus.includes('national gallery'))) return true;
        if (id === 'nmk' && (mus.includes('국립중앙박물관') || mus.includes('간송') || mus.includes('사기장') || akr.includes('김홍도') || akr.includes('정선') || akr.includes('신윤복') || akr.includes('강세황'))) return true;
        if (id === 'rijksmuseum' && (mus.includes('암스테르담') || mus.includes('rijks'))) return true;
        if (id === 'tate' && (mus.includes('테이트') || mus.includes('tate'))) return true;

        // 2. Representative Artist Collection matching
        if (mArtists.some(artName => akr.includes(artName) || artName.includes(akr))) return true;

        return false;
      }});

      document.getElementById('museumGridTitle').textContent = `${{m.name_kr}} 대표 컬렉션`;
      document.getElementById('museumWorkCount').textContent = `${{matched.length}} ITEMS EXHIBITED`;

      const grid = document.getElementById('museumArtGrid');
      if (matched.length === 0) {{
        grid.innerHTML = `<div style="grid-column: 1/-1; padding: 48px; text-align: center; color: var(--lds-text-muted);">미술관 컬렉션을 동기화 중입니다.</div>`;
        return;
      }}

      grid.innerHTML = matched.map(art => {{
        const thumb = art.thumbnail_url || art.image_url || `assets/featured/thumbs/${{art.id}}.webp`;
        return `
          <div class="art-flat-card">
            <div class="art-flat-thumb">
              <img class="art-flat-img" src="${{thumb}}" alt="${{art.title_kr}}" loading="lazy" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'300\\' height=\\'200\\'%3E%3Crect width=\\'100%25\\' height=\\'100%25\\' fill=\\'%230f172a\\'%2F%3E%3C%2Fsvg%3E'">
              <span class="art-flat-badge">${{art.year || '시기 미상'}}</span>
            </div>
            <div class="art-flat-info">
              <a href="artwork.html?id=${{art.id || art.work_id}}" class="art-flat-title">${{art.title_kr}}</a>
              <div class="art-flat-artist">${{art.artist_name_kr || art.artist || '거장 미상'}}</div>
              <div class="art-flat-actions">
                <a href="artwork.html?id=${{art.id || art.work_id}}" class="art-flat-btn">작품 상세</a>
                <a href="artwork.html?id=${{art.id || art.work_id}}&mode=presentation" class="art-flat-btn">갤러리모드</a>
              </div>
            </div>
          </div>
        `;
      }}).join('');
    }}

    window.addEventListener('DOMContentLoaded', initMuseumPavilion);
  </script>
</body>
</html>
"""

with open('museum.html', 'w', encoding='utf-8') as f:
    f.write(museum_html)

print("museum.html successfully overhauled into Grand Theme Pavilion with authentic photos and 7,865+ works federation.")
