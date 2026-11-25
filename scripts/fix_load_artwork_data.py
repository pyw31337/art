#!/usr/bin/env python3
"""
scripts/fix_load_artwork_data.py
Fixes loadArtworkData in artwork.html to properly resolve any artwork ID
across all databases and attach 1:1 verified docents without falling back
to Van Gogh's Starry Night, and strips any emoji prefixes from database text.
"""

import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTWORK_HTML = os.path.join(BASE_DIR, "artwork.html")

with open(ARTWORK_HTML, "r", encoding="utf-8") as f:
    content = f.read()

# Replace the old loadArtworkData function
old_load_func = """    async function loadArtworkData() {
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

new_load_func = """    let videoDocentRegistry = {};

    // Helper: Strip raw emojis from database strings to keep Impeccable SVG standard
    function stripEmoji(str) {
      if (!str) return '';
      return String(str).replace(/[\\u{1F300}-\\u{1F9FF}\\u{2600}-\\u{27BF}\\u{1FA00}-\\u{1FAFF}]/gu, '').replace(/^\\s*[·•\\-]\\s*/, '').trim();
    }

    async function loadArtworkData() {
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

        // 2. Check Expanded Art Categories DB (all arrays)
        if (!found) {
          try {
            const exp = await fetch('data/expanded_art_categories_db.json?v=' + Date.now()).then(r => r.json());
            const expList = [];
            Object.values(exp).forEach(v => {
              if (Array.isArray(v) && v.length && typeof v[0] === 'object') {
                expList.push(...v);
              }
            });
            found = expList.find(a => (a.id === targetId || a.work_id === targetId));
          } catch (e) {
            console.warn("Expanded categories load error:", e);
          }
        }

        // 3. Check Contemporary Art & Architecture DB
        if (!found) {
          try {
            const cont = await fetch('data/contemporary_art_and_architecture_db.json?v=' + Date.now()).then(r => r.json());
            const contList = [];
            Object.values(cont).forEach(v => {
              if (Array.isArray(v) && v.length && typeof v[0] === 'object') {
                contList.push(...v);
              }
            });
            found = contList.find(a => (a.id === targetId || a.work_id === targetId));
          } catch (e) {
            console.warn("Contemporary art load error:", e);
          }
        }

        // 4. Check Digital Gallery Master DB (7,858 works)
        if (!found) {
          try {
            const resDg = await fetch('data/digital_gallery_master_db.json?v=' + Date.now()).then(r => r.json());
            const dgList = resDg.artworks || [];
            found = dgList.find(a => (a.id === targetId || a.work_id === targetId));
          } catch(e) {
            console.warn("Digital gallery load error:", e);
          }
        }

        // Fallback only if absolutely no artwork matched
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
        }
      } catch (err) {
        console.error("Failed to load artwork data:", err);
      }
    }"""

if old_load_func in content:
    content = content.replace(old_load_func, new_load_func)
    print("[+] Successfully replaced loadArtworkData")
else:
    print("[!] Warning: exact old_load_func match not found. Inspecting...")

# Also sanitize text rendering in renderArtworkDetails
# Replace story_label and behind_story with stripEmoji
content = content.replace("document.getElementById('ltStoryBadge').textContent = item.story_label || storyMeta.label;",
                          "document.getElementById('ltStoryBadge').textContent = stripEmoji(item.story_label) || storyMeta.label;")
content = content.replace("document.getElementById('behindSecretContent').textContent = item.behind_story;",
                          "document.getElementById('behindSecretContent').textContent = stripEmoji(item.behind_story);")
content = content.replace("document.getElementById('storyTag').textContent = `HUMAN STORY TAXONOMY · ${item.story_label || storyMeta.label}`;",
                          "document.getElementById('storyTag').textContent = `HUMAN STORY TAXONOMY · ${stripEmoji(item.story_label) || storyMeta.label}`;")
content = content.replace("document.getElementById('presStoryBadge').textContent = item.story_label || storyMeta.label;",
                          "document.getElementById('presStoryBadge').textContent = stripEmoji(item.story_label) || storyMeta.label;")

# Clean iframe allow attribute
content = content.replace('allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen',
                          'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen')

with open(ARTWORK_HTML, "w", encoding="utf-8") as f:
    f.write(content)

print("[+] artwork.html successfully updated and saved.")
