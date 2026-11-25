#!/usr/bin/env python3
"""
scripts/sync_all_featured_to_r2.py
Fetches clean 1200px images via Special:FilePath for all featured masterpieces,
converts them to WebP (UHD & Thumbnail), saves local copies in assets/featured/,
uploads them to Cloudflare R2 bucket letsart-masterpieces,
and updates expanded_art_categories_db.json, contemporary_art_and_architecture_db.json,
and art_paintings_master_db.json with permanent R2 CDN URLs.
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

HEADERS = {'User-Agent': 'LetsArt/1.0 (https://pyw31337.github.io/art/; contact: pyw31337@gmail.com)'}

# Exact Wikimedia File names or direct museum URLs
TARGET_MAP = {
    # Sculptures
    "sculpt_rodin_thinker": "The_Thinker,_Rodin.jpg",
    "sculpt_nike_samothrace": "Nike_of_Samothrace,_Paris,_Louvre.jpg",
    "sculpt_giacometti_walking_man": "Alberto_Giacometti_par_sa_femme_Annette_©_Succession_Alberto_Giacometti_(Fondation_Giacometti,_Paris_+_ADAGP,_Paris)_2019.jpg",
    
    # Asian Art & Korean National Treasures
    "asian_jeongseon_inwang": "Inwangjesaekdo.jpg",
    "asian_shin_yunbok_beauty": "Hyewon-Miindo.jpg",
    "asian_hokusai_great_wave": "Tsunami_by_hokusai_19th_century.jpg",
    "asian_white_porcelain_moon_jar": "White_Porcelain_Moon_Jar_(National_Treasure_No._262)_01.jpg",
    
    # Prints & Drawings
    "print_durer_melencolia": "Dürer_Melancholia_I.jpg",
    "print_escher_relativity": "Escher's_Relativity.jpg",
    
    # Photography
    "photo_bresson_gare_saint_lazare": "Behind_the_Gare_Saint-Lazare.jpg",
    "photo_ansel_adams_tetons": "Adams_The_Tetons_and_the_Snake_River.jpg",
    
    # Craft & Decorative
    "craft_celadon_melon_bottle": "Celadon_inlaid_peony_and_chrysanthemum_pattern_melon-shaped_bottle.jpg",
    "craft_lalique_dragonfly_brooch": "Dragonfly_broche_(René_Lalique,_foto_as_of_2013).jpg",
    
    # Media & Installation Art
    "media_namjune_the_more_the_better": "The_More,_the_Better_(다다익선(多多益善))_백남준_PAIK_Namjune(1932~2006).jpg",
    "media_duchamp_fountain": "Duchamp_Fountaine.jpg",
    
    # Contemporary Art & Architecture
    "cont_art_david_hockney": "David_Hockney_2017_at_Flash_Expo.jpg",
    "cont_art_yayoi_kusama": "Yayoi_Kusama,_Pumpkin,_2015_(37171698741).jpg",
    "cont_art_lee_ufan": "Lee_Ufan.jpg",
    "arch_zaha_hadid_ddp": "Dongdaemun_Design_Plaza_at_night,_Seoul,_Korea.jpg",
    "arch_tadao_ando_church_of_light": "Ibaraki_Kasugaoka_Church_20080914.jpg",
    "arch_frank_gehry_bilbao": "Guggenheim-bilbao-jan05.jpg",
    
    # Master Paintings
    "art_starry_night": "Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg",
    "art_mona_lisa": "Mona_Lisa,_by_Leonardo_da_Vinci,_from_C2RMF_retouched.jpg",
    "art_picasso_demoiselles": "Les_Demoiselles_d'Avignon.jpg",
    "art_dali_persistence_of_memory": "The_Persistence_of_Memory.jpg",
    "art_delacroix_liberty": "Eugène_Delacroix_-_La_liberté_guidant_le_peuple.jpg",
    "art_seurat_grande_jatte": "A_Sunday_on_La_Grande_Jatte,_Georges_Seurat,_1884.jpg",
    "art_botticelli_venus": "Sandro_Botticelli_-_La_nascita_di_Venere_-_Google_Art_Project_-_edited.jpg",
    "art_velazquez_meninas": "Las_Meninas,_by_Diego_Velázquez,_from_Prado_in_Google_Earth.jpg",
    "art_munch_scream": "Edvard_Munch,_1893,_The_Scream,_oil,_tempera_and_pastel_on_cardboard,_91_x_73_cm,_National_Gallery_of_Norway.jpg",
    "art_klimt_the_kiss": "The_Kiss_-_Gustav_Klimt_-_Google_Cultural_Institute.jpg",
    "paint_sargent_001": "https://images.metmuseum.org/crd/images/web-large/DT1432.jpg",
    "paint_anthonissen_whale": "Anthonissen_Hendrik_van_1606-1660_02.jpg",
    "paint_picasso_guitarist": "Old_guitarist_chicago.jpg"
}

def download_bytes_for_item(fn_or_url):
    if fn_or_url.startswith("http"):
        req = urllib.request.Request(fn_or_url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=12) as r:
            return r.read()
    
    # Try Commons Special:FilePath with 1200px width
    encoded_fn = urllib.parse.quote(fn_or_url)
    urls_to_try = [
        f"https://commons.wikimedia.org/wiki/Special:FilePath/{encoded_fn}?width=1200",
        f"https://commons.wikimedia.org/wiki/Special:FilePath/{encoded_fn}?width=800",
        f"https://en.wikipedia.org/wiki/Special:FilePath/{encoded_fn}?width=1200",
        f"https://en.wikipedia.org/wiki/Special:FilePath/{encoded_fn}?width=800"
    ]
    
    for u in urls_to_try:
        try:
            req = urllib.request.Request(u, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=10) as r:
                data = r.read()
                if len(data) > 1000:
                    return data
        except Exception:
            continue
            
    return None

def process_and_upload(item_id, fn_or_url):
    local_uhd = os.path.join(ASSETS_DIR, f"{item_id}.webp")
    local_thumb = os.path.join(ASSETS_THUMB_DIR, f"{item_id}.webp")
    
    uhd_key = f"featured/{item_id}.webp"
    thumb_key = f"featured/thumbs/{item_id}.webp"
    
    # Check if local exists already
    img_data = None
    if os.path.exists(local_uhd):
        with open(local_uhd, "rb") as f:
            uhd_bytes = f.read()
        with open(local_thumb, "rb") as f:
            thumb_bytes = f.read()
    else:
        print(f"[*] Downloading: {item_id} ({fn_or_url})...")
        raw_bytes = download_bytes_for_item(fn_or_url)
        if not raw_bytes:
            print(f"  [X] Failed to download {item_id}")
            return None
            
        im = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
        
        # 1. UHD WebP
        im_uhd = im.copy()
        im_uhd.thumbnail((1400, 1400), Image.Resampling.LANCZOS)
        out_uhd = io.BytesIO()
        im_uhd.save(out_uhd, format="WEBP", quality=85, method=4)
        uhd_bytes = out_uhd.getvalue()
        with open(local_uhd, "wb") as f:
            f.write(uhd_bytes)
            
        # 2. Thumbnail WebP
        im_thumb = im.copy()
        im_thumb.thumbnail((440, 440), Image.Resampling.LANCZOS)
        out_thumb = io.BytesIO()
        im_thumb.save(out_thumb, format="WEBP", quality=80, method=4)
        thumb_bytes = out_thumb.getvalue()
        with open(local_thumb, "wb") as f:
            f.write(thumb_bytes)
            
    # Upload to R2
    try:
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
        print(f"  [+] Uploaded to R2: {item_id} -> {R2_PUBLIC_BASE}/{thumb_key}")
    except Exception as e:
        print(f"  [!] R2 upload failed for {item_id}: {e}")
        
    return {
        "image_url": f"{R2_PUBLIC_BASE}/{uhd_key}",
        "thumbnail_url": f"{R2_PUBLIC_BASE}/{thumb_key}",
        "local_image": f"assets/featured/{item_id}.webp",
        "local_thumb": f"assets/featured/thumbs/{item_id}.webp"
    }

def main():
    print("[*] Starting Full Featured Image Sync to R2...")
    url_map = {}
    for iid, src in TARGET_MAP.items():
        res = process_and_upload(iid, src)
        if res:
            url_map[iid] = res
            
    print(f"\n[*] Uploaded {len(url_map)} items to R2. Updating JSON databases...")
    
    db_files = [
        os.path.join(DATA_DIR, "expanded_art_categories_db.json"),
        os.path.join(DATA_DIR, "contemporary_art_and_architecture_db.json"),
        os.path.join(DATA_DIR, "art_paintings_master_db.json")
    ]
    
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
                    if iid in url_map:
                        item["image_url"] = url_map[iid]["image_url"]
                        item["thumbnail_url"] = url_map[iid]["thumbnail_url"]
                        item["local_image_url"] = url_map[iid]["local_image"]
                        item["local_thumbnail_url"] = url_map[iid]["local_thumb"]
                        modified = True
                        
        if modified:
            with open(db_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"[+] Updated {os.path.basename(db_path)}")
            
    print("\n[★] All featured masterpieces successfully synced to R2!")

if __name__ == "__main__":
    main()
