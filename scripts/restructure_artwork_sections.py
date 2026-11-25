with open('artwork.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Current order of sections in content-sheet-inner:
# Card 1: Masterpiece Overview + Specs + Voice Docent + Karaoke + #artistPeopleContainer
# Card 2: Behind Stories + Human Story Taxonomy
# Card 3: Curatorial Commentary + Color Palette
# Card 4: Video Docent Cinema Hub + Verified Resources Platform Dock

# New desired order requested by user:
# SECTION 1: MASTERPIECE FOCUS (작품에 관한 설명을 상단에 몰아서 배치)
#   - Title, Specs (Year, Medium, Dimension, Museum)
#   - Voice Docent Station + Karaoke Synchronized Script Dock
#   - Behind Stories & Restoration Secret Card
#   - Human Story Taxonomy Card
#   - Curatorial In-depth Commentary & Historical Background
#   - Masterpiece Color Palette
#
# SECTION 2: ARTIST FOCUS (하단으로 작가에 관한 컨텐츠 배열)
#   - Let's People Master Dossier (#artistPeopleContainer)
#
# SECTION 3: MULTIMEDIA & SOURCES (맨 하단으로 관련 컨텐츠나 출처 정보)
#   - Video Docent Cinema Player
#   - Verified Resources & Academic Museum Archive Hub

# Let's extract the pieces cleanly
start_inner = html.find('<div class="content-sheet-inner">')
end_inner = html.find('</div>\n  </div>\n\n  <!-- ========================================================\n       PRESENTATION GALLERY')

inner_block = html[start_inner:end_inner]

# 1. Move #artistPeopleContainer out of Card 1 and put into its own dedicated section
# Find #artistPeopleContainer
target_people_div = '<!-- Let\'s People 거장 심층 프로필 연동 컨테이너 -->\n        <div id="artistPeopleContainer"></div>\n      </div>'
assert target_people_div in inner_block, "target_people_div not found in inner_block"

# Replace target_people_div with just closing the card
inner_block_cleaned = inner_block.replace(target_people_div, '</div>')

# 2. Add Museum Photo & Details to Specification Grid
# Currently specMuseum is just text. Let's make it look richer with museum architecture photo badge link
old_spec_museum = """          <div class="spec-pill">
            <span class="spec-label">소장처</span>
            <span class="spec-val" id="specMuseum">소장처 정보</span>
          </div>"""

new_spec_museum = """          <div class="spec-pill">
            <span class="spec-label">소장처 및 소장관</span>
            <div style="display:flex; align-items:center; gap:8px;">
              <span class="spec-val" id="specMuseum">소장처 정보</span>
            </div>
          </div>"""

inner_block_cleaned = inner_block_cleaned.replace(old_spec_museum, new_spec_museum)

# Now restructure sections inside inner_block
# We want:
# Card 1 (Specs & Voice & Karaoke)
# Card 2 (Behind Story & Human Story)
# Card 3 (Curatorial Commentary, History, Palette)
# --- Then Dedicated Section: ARTIST DOSSIER (하단 작가 집중 컨텐츠) ---
# --- Then Section 4: MULTIMEDIA VIDEO DOCENT & VERIFIED PLATFORM SOURCES (맨 하단 출처 & 미디어) ---

artist_section_html = """
      <!-- ========================================================
           SECTION 2: ARTIST DOSSIER & LIFE LEGACY (시대의 거장 프로필)
           ======================================================== -->
      <div class="museum-sheet-card" style="border-bottom:1px solid rgba(226, 232, 240, 0.65) !important;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
          <h2 class="article-headline" style="margin-bottom:0; display:flex; align-items:center; gap:8px;">
            <svg class="icon" style="color:#2563eb;"><use href="#i-user"></use></svg>
            <span>시대의 거장 프로필 & 예술적 계보</span>
          </h2>
          <span class="lds-mono" style="font-size:11px; color:#64748b;">LET'S PEOPLE FEDERATED DOSSIER</span>
        </div>
        <div id="artistPeopleContainer"></div>
      </div>
"""

# Place artist_section_html right before Card 4 (docentHubSection)
card4_marker = '<div class="docent-cinema-section" id="docentHubSection">'
assert card4_marker in inner_block_cleaned, "card4_marker not found"

new_inner_block = inner_block_cleaned.replace(card4_marker, artist_section_html + '\n      ' + card4_marker)

# Replace in html
html = html[:start_inner] + new_inner_block + html[end_inner:]

with open('artwork.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("artwork.html sections successfully restructured (Work top -> Artist mid -> Sources bottom).")
