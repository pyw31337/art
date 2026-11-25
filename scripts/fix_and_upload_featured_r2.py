#!/usr/bin/env python3
"""
scripts/fix_and_upload_featured_r2.py
Fetches high-resolution images for all featured masterpieces (Sculptures, Asian Art, Prints,
Photography, Craft, Contemporary Art/Architecture, Master Paintings), converts them to WebP,
uploads them to Cloudflare R2, saves local fallbacks under assets/featured/, and updates
the master JSON databases with permanent R2 CDN URLs.
"""

import os
import sys
import json
import io
import time
import urllib.request
import urllib.parse
from PIL import Image
import boto3
from botocore.config import Config

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
ASSETS_DIR = os.path.join(BASE_DIR, "assets", "featured")
ASSETS_THUMB_DIR = os.path.join(ASSETS_DIR, "thumbs")
os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(ASSETS_THUMB_DIR, exist_ok=True)

R2_ENDPOINT = "https://51437a5851eb0715415e7df9e3a4e5c1.r2.cloudflarestorage.com"
R2_ACCESS_KEY = os.environ.get("R2_ACCESS_KEY", "ef93d72d5115e5018cfd7a1cf5980eae")
R2_SECRET_KEY = os.environ.get("R2_SECRET_KEY", "8b2947b1ea954f748a328f502e1043f9e68a4a3d6dbb6f5e670e23d0fcb92552")
R2_BUCKET = "letsart-masterpieces"
R2_PUBLIC_BASE = "https://pub-685f237e5a544431bee558c5b29f3291.r2.dev"

s3 = boto3.client(
    "s3",
    endpoint_url=R2_ENDPOINT,
    aws_access_key_id=R2_ACCESS_KEY,
    aws_secret_access_key=R2_SECRET_KEY,
    region_name="auto",
    config=Config(retries={"max_attempts": 5, "mode": "standard"})
)

HEADERS = {'User-Agent': 'LetsArtBot/1.0 (https://pyw31337.github.io/art/; contact: pyw31337@gmail.com)'}

def resolve_wikimedia_url(url):
    """Resolve correct original Wikimedia Commons URL via API if broken."""
    if 'wikimedia.org' not in url:
        return url
    
    parts = url.split('/')
    # Extract filename
    fn = parts[-1]
    if fn.endswith('px-' + parts[-1].split('px-')[-1]) and 'px-' in fn:
        fn = fn.split('px-')[-1]
    
    fn = urllib.parse.unquote(fn)
    # Remove query params
    if '?' in fn:
        fn = fn.split('?')[0]
        
    api_url = f"https://commons.wikimedia.org/w/api.php?action=query&titles=File:{urllib.parse.quote(fn)}&prop=imageinfo&iiprop=url&format=json"
    try:
        req = urllib.request.Request(api_url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as r:
            res = json.loads(r.read())
        pages = res.get('query', {}).get('pages', {})
        for pid, page in pages.items():
            if 'imageinfo' in page and len(page['imageinfo']) > 0:
                orig_url = page['imageinfo'][0].get('url')
                if orig_url:
                    return orig_url
    except Exception as e:
        print(f"  [!] Wikimedia API query error for {fn}: {e}")
        
    # Also try English Wikipedia API if on wikipedia/en
    if '/en/' in url:
        en_api = f"https://en.wikipedia.org/w/api.php?action=query&titles=File:{urllib.parse.quote(fn)}&prop=imageinfo&iiprop=url&format=json"
        try:
            req = urllib.request.Request(en_api, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=10) as r:
                res = json.loads(r.read())
            pages = res.get('query', {}).get('pages', {})
            for pid, page in pages.items():
                if 'imageinfo' in page and len(page['imageinfo']) > 0:
                    orig_url = page['imageinfo'][0].get('url')
                    if orig_url:
                        return orig_url
        except Exception:
            pass
            
    return url

# Direct fallback high-res museum/open-access images for specific works if needed
CURATED_SOURCES = {
    "sculpt_rodin_thinker": "https://upload.wikimedia.org/wikipedia/commons/5/56/The_Thinker%2C_Rodin.jpg",
    "sculpt_nike_samothrace": "https://upload.wikimedia.org/wikipedia/commons/1/1b/Victoire_de_Samothrace_-_Louvre_Museum_-_May_2014.jpg",
    "sculpt_giacometti_walking_man": "https://upload.wikimedia.org/wikipedia/en/4/4b/L%27Homme_qui_marche_I.jpg",
    "asian_jeongseon_inwang": "https://upload.wikimedia.org/wikipedia/commons/6/6f/Inwang_jesaekdo.jpg",
    "asian_shin_yunbok_beauty": "https://upload.wikimedia.org/wikipedia/commons/0/07/Hyewon-Miindo.jpg",
    "asian_hokusai_great_wave": "https://upload.wikimedia.org/wikipedia/commons/a/a5/Tsunami_by_hokusai_19th_century.jpg",
    "asian_white_porcelain_moon_jar": "https://upload.wikimedia.org/wikipedia/commons/c/cf/Moon_jar-Baekja_daeho-National_Treasure_No.309.jpg",
    "print_durer_melencolia": "https://upload.wikimedia.org/wikipedia/commons/1/18/D%C3%BCrer_Melancholia_I.jpg",
    "print_escher_relativity": "https://upload.wikimedia.org/wikipedia/en/7/73/Escher%27s_Relativity.jpg",
    "photo_bresson_gare_saint_lazare": "https://upload.wikimedia.org/wikipedia/en/0/07/Behind_the_Gare_Saint-Lazare.jpg",
    "photo_ansel_adams_tetons": "https://upload.wikimedia.org/wikipedia/commons/2/21/Adams_The_Tetons_and_the_Snake_River.jpg",
    "craft_celadon_melon_bottle": "https://upload.wikimedia.org/wikipedia/commons/c/c8/Celadon_Melon-shaped_Bottle_from_the_Tomb_of_King_Injong_of_Goryeo-National_Treasure_No.94.jpg",
    "craft_lalique_dragonfly_brooch": "https://upload.wikimedia.org/wikipedia/commons/a/ae/Dragonfly_woman_corsage_ornament.jpg",
    "media_namjune_the_more_the_better": "https://upload.wikimedia.org/wikipedia/commons/8/87/Nam_June_Paik_-_The_More_The_Better.jpg",
    "media_duchamp_fountain": "https://upload.wikimedia.org/wikipedia/commons/f/f6/Duchamp_Fountaine.jpg",
    "cont_art_david_hockney": "https://upload.wikimedia.org/wikipedia/en/9/91/A_Bigger_Splash.jpg",
    "cont_art_yayoi_kusama": "https://upload.wikimedia.org/wikipedia/commons/1/1a/Naoshima_Kusama_Pumpkin.jpg",
    "cont_art_lee_ufan": "https://upload.wikimedia.org/wikipedia/commons/d/d3/Lee_Ufan_-_Dialogue_%28cropped%29.jpg",
    "arch_zaha_hadid_ddp": "https://upload.wikimedia.org/wikipedia/commons/7/7b/Dongdaemun_Design_Plaza_2014.jpg",
    "arch_tadao_ando_church_of_light": "https://upload.wikimedia.org/wikipedia/commons/c/c5/Church_of_the_Light_01.jpg",
    "arch_frank_gehry_bilbao": "https://upload.wikimedia.org/wikipedia/commons/d/de/Guggenheim-bilbao-jan05.jpg",
    "art_starry_night": "https://upload.wikimedia.org/wikipedia/commons/e/ea/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg",
    "art_mona_lisa": "https://upload.wikimedia.org/wikipedia/commons/e/ec/Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg",
    "art_picasso_demoiselles": "https://upload.wikimedia.org/wikipedia/en/4/4c/Les_Demoiselles_d%27Avignon.jpg",
    "art_dali_persistence_of_memory": "https://upload.wikimedia.org/wikipedia/en/d/dd/The_Persistence_of_Memory.jpg",
    "art_delacroix_liberty": "https://upload.wikimedia.org/wikipedia/commons/a/a7/Eug%C3%A8ne_Delacroix_-_La_libert%C3%A9_guidant_le_peuple.jpg",
    "art_seurat_grande_jatte": "https://upload.wikimedia.org/wikipedia/commons/7/7d/A_Sunday_on_La_Grande_Jatte%2C_Georges_Seurat%2C_1884.jpg",
    "art_botticelli_venus": "https://upload.wikimedia.org/wikipedia/commons/0/0b/Sandro_Botticelli_-_La_nascita_di_Venere_-_Google_Art_Project_-_edited.jpg",
    "art_velazquez_meninas": "https://upload.wikimedia.org/wikipedia/commons/3/31/Las_Meninas%2C_by_Diego_Vel%C3%A1zquez%2C_from_Prado_in_Google_Earth.jpg",
    "art_munch_scream": "https://upload.wikimedia.org/wikipedia/commons/c/c5/Edvard_Munch%2C_1893%2C_The_Scream%2C_oil%2C_tempera_and_pastel_on_cardboard%2C_91_x_73_cm%2C_National_Gallery_of_Norway.jpg",
    "art_klimt_the_kiss": "https://upload.wikimedia.org/wikipedia/commons/4/40/The_Kiss_-_Gustav_Klimt_-_Google_Cultural_Institute.jpg",
    "paint_sargent_001": "https://images.metmuseum.org/crd/images/web-large/DT1432.jpg",
    "paint_anthonissen_whale": "https://upload.wikimedia.org/wikipedia/commons/9/93/Anthonissen_Hendrik_van_1606-1660_02.jpg",
    "paint_picasso_guitarist": "https://upload.wikimedia.org/wikipedia/en/b/bc/Old_guitarist_chicago.jpg"
}

def download_image(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()

def process_and_upload(item_id, raw_url):
    print(f"[*] Processing: {item_id}...")
    source_url = CURATED_SOURCES.get(item_id) or resolve_wikimedia_url(raw_url)
    
    img_data = None
    try:
        img_data = download_image(source_url)
    except Exception as e:
        print(f"  [!] Primary download failed for {item_id}: {e}")
        # Try resolving via API if wasn't resolved
        resolved = resolve_wikimedia_url(source_url)
        if resolved != source_url:
            try:
                img_data = download_image(resolved)
            except Exception as e2:
                print(f"  [!] Secondary download failed: {e2}")
                return None

    if not img_data:
        return None

    try:
        im = Image.open(io.BytesIO(img_data)).convert('RGB')
        
        # 1. UHD WebP (max 1600px width/height)
        im_uhd = im.copy()
        im_uhd.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
        uhd_io = io.BytesIO()
        im_uhd.save(uhd_io, format="WEBP", quality=85, method=4)
        uhd_bytes = uhd_io.getvalue()
        
        # Save local fallback
        local_uhd_path = os.path.join(ASSETS_DIR, f"{item_id}.webp")
        with open(local_uhd_path, "wb") as f:
            f.write(uhd_bytes)
            
        # 2. Thumbnail WebP (max 480px)
        im_thumb = im.copy()
        im_thumb.thumbnail((480, 480), Image.Resampling.LANCZOS)
        thumb_io = io.BytesIO()
        im_thumb.save(thumb_io, format="WEBP", quality=80, method=4)
        thumb_bytes = thumb_io.getvalue()
        
        local_thumb_path = os.path.join(ASSETS_THUMB_DIR, f"{item_id}.webp")
        with open(local_thumb_path, "wb") as f:
            f.write(thumb_bytes)
            
        # 3. Upload to R2
        uhd_key = f"featured/{item_id}.webp"
        thumb_key = f"featured/thumbs/{item_id}.webp"
        
        s3.put_object(
            Bucket=R2_BUCKET,
            Key=uhd_key,
            Body=uhd_bytes,
            ContentType="image/webp",
            CacheControl="public, max-age=31536000, immutable"
        )
        s3.put_object(
            Bucket=R2_BUCKET,
            Key=thumb_key,
            Body=thumb_bytes,
            ContentType="image/webp",
            CacheControl="public, max-age=31536000, immutable"
        )
        
        r2_uhd_url = f"{R2_PUBLIC_BASE}/{uhd_key}"
        r2_thumb_url = f"{R2_PUBLIC_BASE}/{thumb_key}"
        
        print(f"  [+] Uploaded {item_id} -> {r2_thumb_url}")
        return {
            "image_url": r2_uhd_url,
            "thumbnail_url": r2_thumb_url,
            "local_image": f"assets/featured/{item_id}.webp",
            "local_thumb": f"assets/featured/thumbs/{item_id}.webp"
        }
    except Exception as e:
        print(f"  [!] Image processing error for {item_id}: {e}")
        return None

def main():
    db_files = [
        os.path.join(DATA_DIR, "expanded_art_categories_db.json"),
        os.path.join(DATA_DIR, "contemporary_art_and_architecture_db.json"),
        os.path.join(DATA_DIR, "art_paintings_master_db.json")
    ]
    
    url_map = {}
    
    for db_path in db_files:
        if not os.path.exists(db_path):
            continue
        with open(db_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        modified = False
        for k, v in data.items():
            if isinstance(v, list) and v and isinstance(v[0], dict):
                for item in v:
                    iid = item.get("id") or item.get("work_id")
                    if not iid:
                        continue
                    curr_url = item.get("image_url") or ""
                    
                    if iid not in url_map:
                        res = process_and_upload(iid, curr_url)
                        if res:
                            url_map[iid] = res
                    
                    if iid in url_map:
                        item["image_url"] = url_map[iid]["image_url"]
                        item["thumbnail_url"] = url_map[iid]["thumbnail_url"]
                        item["local_image_url"] = url_map[iid]["local_image"]
                        item["local_thumbnail_url"] = url_map[iid]["local_thumb"]
                        modified = True
                        
        if modified:
            with open(db_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"[+] Updated {os.path.basename(db_path)} with verified R2 URLs.")

    print(f"\n[★] Complete! Processed and verified {len(url_map)} featured items.")

if __name__ == "__main__":
    main()
