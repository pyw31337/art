import os, json, urllib.request, re, time
from PIL import Image

with open('data/themes_spec.json', 'r', encoding='utf-8') as f:
    themes = json.load(f)

os.makedirs('assets/themes', exist_ok=True)

def get_wiki_image_url(query):
    # Try direct filename search if query ends with image extension
    if query.endswith(('.jpg', '.JPG', '.png', '.PNG', '.webp')):
        url = f'https://commons.wikimedia.org/w/api.php?action=query&titles=File:{urllib.parse.quote(query)}&prop=imageinfo&iiprop=url&iiurlwidth=1920&format=json'
        req = urllib.request.Request(url, headers={'User-Agent': 'LetsArt/1.0 (dev@letsart.io)'})
        try:
            with urllib.request.urlopen(req) as r:
                d = json.loads(r.read().decode('utf-8'))
                for p in d['query']['pages'].values():
                    if 'imageinfo' in p:
                        info = p['imageinfo'][0]
                        return info.get('thumburl') or info.get('url')
        except Exception:
            pass

    # Search by keywords
    clean_q = re.sub(r'\(.*?\)', '', query).strip()
    search_url = f'https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(clean_q)}&srnamespace=6&srlimit=1&format=json'
    req = urllib.request.Request(search_url, headers={'User-Agent': 'LetsArt/1.0 (dev@letsart.io)'})
    try:
        with urllib.request.urlopen(req) as r:
            d = json.loads(r.read().decode('utf-8'))
            results = d.get('query', {}).get('search', [])
            if not results:
                return None
            title = results[0]['title']
        
        info_url = f'https://commons.wikimedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=imageinfo&iiprop=url&iiurlwidth=1920&format=json'
        req2 = urllib.request.Request(info_url, headers={'User-Agent': 'LetsArt/1.0 (dev@letsart.io)'})
        with urllib.request.urlopen(req2) as r2:
            d2 = json.loads(r2.read().decode('utf-8'))
            for p in d2['query']['pages'].values():
                if 'imageinfo' in p:
                    info = p['imageinfo'][0]
                    return info.get('thumburl') or info.get('url')
    except Exception as e:
        pass
    return None

def process_and_save_webp(src_path_or_bytes, dest_path, max_dim=2560):
    try:
        if isinstance(src_path_or_bytes, bytes):
            import io
            im = Image.open(io.BytesIO(src_path_or_bytes))
        else:
            im = Image.open(src_path_or_bytes)
        
        im = im.convert('RGB')
        w, h = im.size
        if w > max_dim or h > max_dim:
            if w > h:
                new_w = max_dim
                new_h = int(h * (max_dim / w))
            else:
                new_h = max_dim
                new_w = int(w * (max_dim / h))
            im = im.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        im.save(dest_path, 'WEBP', quality=82, method=4)
        return True
    except Exception as e:
        print(f"Error processing image for {dest_path}: {e}")
        return False

# Master catalog to save
catalog = {
    "version": "1.0.0",
    "updated_at": "2026-11-25T15:40:00+09:00",
    "curated_themes": []
}

for theme in themes:
    t_id = theme['id']
    theme_dir = os.path.join('assets/themes', t_id)
    os.makedirs(theme_dir, exist_ok=True)
    
    theme_record = {
        "id": t_id,
        "title_kr": theme['title_kr'],
        "title_en": theme['title_en'],
        "subtitle": theme['subtitle'],
        "description": theme['description'],
        "color_accent": theme['color_accent'],
        "color_tag": theme['color_tag'],
        "badge": theme['badge'],
        "category": theme['category'],
        "default_bgm": theme['default_bgm'],
        "items_count": len(theme['items']),
        "hero_image": f"assets/themes/{t_id}/{theme['items'][0]['id']}.webp",
        "items": []
    }
    
    print(f"\nProcessing theme: {theme['title_kr']} ({t_id})...")
    
    for item in theme['items']:
        i_id = item['id']
        dest_webp = os.path.join(theme_dir, f"{i_id}.webp")
        local_rel = f"assets/themes/{t_id}/{i_id}.webp"
        
        item_entry = {
            "id": i_id,
            "title": item['title'],
            "artist": item['artist'],
            "image_url": local_rel,
            "thumbnail_url": local_rel,
            "theme_id": t_id,
            "color_tag": theme['color_tag']
        }
        
        if os.path.exists(dest_webp) and os.path.getsize(dest_webp) > 10000:
            print(f"  [OK:Cached] {i_id}: {item['title']}")
            theme_record["items"].append(item_entry)
            continue
        
        query = item['query']
        # Check if query points to existing local file in assets/featured/
        if query.startswith('assets/featured/') and os.path.exists(query):
            if process_and_save_webp(query, dest_webp):
                print(f"  [OK:Local] {i_id}: {item['title']}")
                theme_record["items"].append(item_entry)
                continue
        
        # Otherwise query Wikimedia
        time.sleep(0.8) # Polite delay
        img_url = get_wiki_image_url(query)
        if img_url:
            try:
                req = urllib.request.Request(img_url, headers={'User-Agent': 'LetsArt/1.0 (dev@letsart.io)'})
                with urllib.request.urlopen(req, timeout=15) as resp:
                    raw_data = resp.read()
                if process_and_save_webp(raw_data, dest_webp):
                    print(f"  [OK:Downloaded] {i_id}: {item['title']} -> {os.path.getsize(dest_webp):,}B")
                    theme_record["items"].append(item_entry)
                    continue
            except Exception as e:
                print(f"  [Fail:Download] {i_id} ({item['title']}): {e}")
        
        # Fallback to local default if download failed
        fallback_candidates = [
            'assets/featured/paint_sargent_001.webp',
            'assets/featured/paint_picasso_guitarist.webp',
            'assets/featured/paint_monet_001.webp',
            'assets/featured/asian_jeongseon_inwang.webp'
        ]
        for cand in fallback_candidates:
            if os.path.exists(cand):
                process_and_save_webp(cand, dest_webp)
                print(f"  [OK:Fallback] {i_id}: {item['title']} (from {cand})")
                theme_record["items"].append(item_entry)
                break
                
    catalog["curated_themes"].append(theme_record)

with open('data/curated_ambient_themes_db.json', 'w', encoding='utf-8') as f:
    json.dump(catalog, f, ensure_ascii=False, indent=2)

print("\nSuccessfully built data/curated_ambient_themes_db.json!")
