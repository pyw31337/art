with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old_css = """.museum-showcase-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
      gap: 16px;
      margin-bottom: 48px;
    }
    .museum-mini-card {
      background: var(--lds-canvas-bg);
      border: 1px solid var(--lds-divider-line);
      border-radius: 4px;
      padding: 16px;
      text-decoration: none;
      color: inherit;
      display: flex;
      flex-direction: column;
      transition: all 0.15s ease;
    }
    .museum-mini-card:hover {
      border-color: var(--lds-brand-600);
      background: var(--lds-surface-subtle);
    }
    .museum-mini-header {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 6px;
    }
    .museum-mini-title {
      font-size: 14px;
      font-weight: 700;
      color: var(--lds-text-strong);
    }
    .museum-mini-city {
      font-size: 11.5px;
      color: var(--lds-text-muted);
      margin-bottom: 8px;
    }
    .museum-mini-tag {
      font-family: var(--lds-font-mono);
      font-size: 11px;
      color: var(--lds-brand-600);
      font-weight: 600;
      margin-top: auto;
      display: flex;
      align-items: center;
      gap: 4px;
    }"""

new_css = """.museum-showcase-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 20px;
      margin-bottom: 48px;
    }
    .museum-mini-card {
      background: #0f172a;
      border: none;
      border-radius: 6px;
      overflow: hidden;
      text-decoration: none;
      color: #ffffff;
      transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.2s ease;
      display: flex;
      flex-direction: column;
      position: relative;
    }
    .museum-mini-card:hover {
      transform: translateY(-3px);
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.25);
    }
    .museum-thumb-box {
      width: 100%;
      height: 140px;
      overflow: hidden;
      position: relative;
    }
    .museum-thumb-img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: transform 0.3s ease;
    }
    .museum-mini-card:hover .museum-thumb-img {
      transform: scale(1.04);
    }
    .museum-thumb-overlay {
      position: absolute;
      inset: 0;
      background: linear-gradient(0deg, rgba(15, 23, 42, 0.95) 0%, rgba(15, 23, 42, 0.2) 60%, transparent 100%);
    }
    .museum-card-body {
      padding: 14px 16px;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .museum-mini-title {
      font-size: 14.5px;
      font-weight: 700;
      color: #ffffff;
    }
    .museum-mini-city {
      font-size: 11.5px;
      color: #94a3b8;
    }
    .museum-mini-tag {
      font-size: 11px;
      color: #60a5fa;
      margin-top: 6px;
      display: flex;
      align-items: center;
      gap: 4px;
      font-weight: 600;
    }"""

assert old_css in html, "old_css not found"
html = html.replace(old_css, new_css)

# Update HTML grid
old_grid_html = """      <div class="museum-showcase-grid">
        <a href="museum.html?id=louvre" class="museum-mini-card">
          <div class="museum-mini-header">
            <svg class="icon" style="color:var(--lds-brand-600);"><use href="#i-museum"/></svg>
            <div class="museum-mini-title">파리 루브르 박물관</div>
          </div>
          <div class="museum-mini-city">프랑스 파리 · 38만 점 소장</div>
          <div class="museum-mini-tag"><span>컬렉션 탐색</span> <svg class="icon" style="width:12px; height:12px;"><use href="#i-arrow-right"/></svg></div>
        </a>

        <a href="museum.html?id=met" class="museum-mini-card">
          <div class="museum-mini-header">
            <svg class="icon" style="color:var(--lds-brand-600);"><use href="#i-museum"/></svg>
            <div class="museum-mini-title">메트로폴리탄 미술관</div>
          </div>
          <div class="museum-mini-city">미국 뉴욕 · 200만 점 소장</div>
          <div class="museum-mini-tag"><span>컬렉션 탐색</span> <svg class="icon" style="width:12px; height:12px;"><use href="#i-arrow-right"/></svg></div>
        </a>

        <a href="museum.html?id=moma" class="museum-mini-card">
          <div class="museum-mini-header">
            <svg class="icon" style="color:var(--lds-brand-600);"><use href="#i-museum"/></svg>
            <div class="museum-mini-title">뉴욕 근대미술관 (MoMA)</div>
          </div>
          <div class="museum-mini-city">미국 뉴욕 · 모더니즘 성전</div>
          <div class="museum-mini-tag"><span>컬렉션 탐색</span> <svg class="icon" style="width:12px; height:12px;"><use href="#i-arrow-right"/></svg></div>
        </a>

        <a href="museum.html?id=orsay" class="museum-mini-card">
          <div class="museum-mini-header">
            <svg class="icon" style="color:var(--lds-brand-600);"><use href="#i-museum"/></svg>
            <div class="museum-mini-title">파리 오르세 미술관</div>
          </div>
          <div class="museum-mini-city">프랑스 파리 · 인상주의 성지</div>
          <div class="museum-mini-tag"><span>컬렉션 탐색</span> <svg class="icon" style="width:12px; height:12px;"><use href="#i-arrow-right"/></svg></div>
        </a>
      </div>"""

new_grid_html = """      <div class="museum-showcase-grid">
        <a href="museum.html?id=louvre" class="museum-mini-card">
          <div class="museum-thumb-box">
            <img class="museum-thumb-img" src="assets/museums/louvre.jpg" alt="파리 루브르 박물관" loading="lazy">
            <div class="museum-thumb-overlay"></div>
          </div>
          <div class="museum-card-body">
            <div class="museum-mini-title">파리 루브르 박물관</div>
            <div class="museum-mini-city">프랑스 파리 · 38만 점 소장</div>
            <div class="museum-mini-tag"><span>테마관 입장</span> <svg class="icon" style="width:12px; height:12px;"><use href="#i-arrow-right"/></svg></div>
          </div>
        </a>

        <a href="museum.html?id=met" class="museum-mini-card">
          <div class="museum-thumb-box">
            <img class="museum-thumb-img" src="assets/museums/met.jpg" alt="메트로폴리탄 미술관" loading="lazy">
            <div class="museum-thumb-overlay"></div>
          </div>
          <div class="museum-card-body">
            <div class="museum-mini-title">메트로폴리탄 미술관</div>
            <div class="museum-mini-city">미국 뉴욕 · 200만 점 소장</div>
            <div class="museum-mini-tag"><span>테마관 입장</span> <svg class="icon" style="width:12px; height:12px;"><use href="#i-arrow-right"/></svg></div>
          </div>
        </a>

        <a href="museum.html?id=moma" class="museum-mini-card">
          <div class="museum-thumb-box">
            <img class="museum-thumb-img" src="assets/museums/moma.jpg" alt="뉴욕 근대미술관 (MoMA)" loading="lazy">
            <div class="museum-thumb-overlay"></div>
          </div>
          <div class="museum-card-body">
            <div class="museum-mini-title">뉴욕 근대미술관 (MoMA)</div>
            <div class="museum-mini-city">미국 뉴욕 맨해튼 · 모더니즘 성전</div>
            <div class="museum-mini-tag"><span>테마관 입장</span> <svg class="icon" style="width:12px; height:12px;"><use href="#i-arrow-right"/></svg></div>
          </div>
        </a>

        <a href="museum.html?id=orsay" class="museum-mini-card">
          <div class="museum-thumb-box">
            <img class="museum-thumb-img" src="assets/museums/orsay.jpg" alt="파리 오르세 미술관" loading="lazy">
            <div class="museum-thumb-overlay"></div>
          </div>
          <div class="museum-card-body">
            <div class="museum-mini-title">파리 오르세 미술관</div>
            <div class="museum-mini-city">프랑스 파리 · 인상주의 성지</div>
            <div class="museum-mini-tag"><span>테마관 입장</span> <svg class="icon" style="width:12px; height:12px;"><use href="#i-arrow-right"/></svg></div>
          </div>
        </a>

        <a href="museum.html?id=prado" class="museum-mini-card">
          <div class="museum-thumb-box">
            <img class="museum-thumb-img" src="assets/museums/prado.jpg" alt="마드리드 프라도 미술관" loading="lazy">
            <div class="museum-thumb-overlay"></div>
          </div>
          <div class="museum-card-body">
            <div class="museum-mini-title">마드리드 프라도 미술관</div>
            <div class="museum-mini-city">스페인 마드리드 · 스페인 회화의 정점</div>
            <div class="museum-mini-tag"><span>테마관 입장</span> <svg class="icon" style="width:12px; height:12px;"><use href="#i-arrow-right"/></svg></div>
          </div>
        </a>

        <a href="museum.html?id=uffizi" class="museum-mini-card">
          <div class="museum-thumb-box">
            <img class="museum-thumb-img" src="assets/museums/uffizi.jpg" alt="피렌체 우피치 미술관" loading="lazy">
            <div class="museum-thumb-overlay"></div>
          </div>
          <div class="museum-card-body">
            <div class="museum-mini-title">피렌체 우피치 미술관</div>
            <div class="museum-mini-city">이탈리아 피렌체 · 르네상스 성소</div>
            <div class="museum-mini-tag"><span>테마관 입장</span> <svg class="icon" style="width:12px; height:12px;"><use href="#i-arrow-right"/></svg></div>
          </div>
        </a>

        <a href="museum.html?id=national_gallery" class="museum-mini-card">
          <div class="museum-thumb-box">
            <img class="museum-thumb-img" src="assets/museums/national_gallery.jpg" alt="런던 내셔널 갤러리" loading="lazy">
            <div class="museum-thumb-overlay"></div>
          </div>
          <div class="museum-card-body">
            <div class="museum-mini-title">런던 내셔널 갤러리</div>
            <div class="museum-mini-city">영국 런던 · 서유럽 회화 명작</div>
            <div class="museum-mini-tag"><span>테마관 입장</span> <svg class="icon" style="width:12px; height:12px;"><use href="#i-arrow-right"/></svg></div>
          </div>
        </a>

        <a href="museum.html?id=nmk" class="museum-mini-card">
          <div class="museum-thumb-box">
            <img class="museum-thumb-img" src="assets/museums/nmk.jpg" alt="국립중앙박물관" loading="lazy">
            <div class="museum-thumb-overlay"></div>
          </div>
          <div class="museum-card-body">
            <div class="museum-mini-title">국립중앙박물관 & 간송미술관</div>
            <div class="museum-mini-city">대한민국 서울 · 국보·보물 전당</div>
            <div class="museum-mini-tag"><span>테마관 입장</span> <svg class="icon" style="width:12px; height:12px;"><use href="#i-arrow-right"/></svg></div>
          </div>
        </a>
      </div>"""

assert old_grid_html in html, "old_grid_html not found"
html = html.replace(old_grid_html, new_grid_html)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html successfully updated with authentic museum architecture photos.")
