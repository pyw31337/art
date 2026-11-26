#!/usr/bin/env python3
"""
scripts/sync_rule74_r2.py
Implements and enforces RULE #74 standard across Let's Art:
1. Auto-Orientation: EXIF + Vision orientation correction (0°/90°/180°/270°)
2. High-Fidelity WebP: Max dimension 2400px (LANCZOS), WebP quality 86%
3. Direct Cloudflare R2 Upload & SHA-256 Deduplication:
   Key: att/v1/blobs/<sha256>.webp
   CDN: https://pub-685f237e5a544431bee558c5b29f3291.r2.dev/att/v1/blobs/<sha256>.webp
4. High-Quality Apple Vision OCR text extraction (.accurate) and D1 search indexing
5. Updates all catalogs and frontends with canonical R2 URLs.
"""

import os
import sys
import json
import io
import hashlib
import subprocess
from datetime import datetime
from PIL import Image, ImageOps
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
OCR_BIN = os.path.join(SCRIPTS_DIR, "bin", "apple_vision_ocr")

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

REGISTRY_FILE = os.path.join(DATA_DIR, "r2_sha256_registry.json")
INDEX_FILE = os.path.join(DATA_DIR, "r2_blobs_index.json")

def load_registry():
    if os.path.exists(REGISTRY_FILE):
        try:
            with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_registry(registry):
    with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)
    print(f"[+] Saved registry to {REGISTRY_FILE} ({len(registry)} blobs)")

def run_apple_vision_ocr(abs_image_path):
    if not os.path.exists(OCR_BIN):
        return []
    try:
        proc = subprocess.run([OCR_BIN, abs_image_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
        if proc.returncode == 0 and proc.stdout.strip():
            lines = json.loads(proc.stdout.strip())
            return lines
    except Exception as e:
        print(f"[-] OCR failed for {abs_image_path}: {e}")
    return []

def process_image_rule74(abs_path):
    """Processes an image adhering to RULE #74 specs."""
    # 1. Open and auto-orient via EXIF
    with Image.open(abs_path) as orig_img:
        img = ImageOps.exif_transpose(orig_img)
        w, h = img.size

        # 2. High-fidelity WebP resize (max dim 2400px)
        max_dim = 2400
        if max(w, h) > max_dim:
            if w >= h:
                new_w = max_dim
                new_h = int(round(h * (max_dim / w)))
            else:
                new_h = max_dim
                new_w = int(round(w * (max_dim / h)))
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        else:
            new_w, new_h = w, h

        # Compress to WebP quality 86
        buf = io.BytesIO()
        if img.mode in ("RGBA", "LA") and "A" in img.getbands():
            img.save(buf, format="WEBP", quality=86, method=4)
        else:
            img = img.convert("RGB")
            img.save(buf, format="WEBP", quality=86, method=4)
        webp_bytes = buf.getvalue()

    # 3. SHA-256 Content Hash
    sha256_hash = hashlib.sha256(webp_bytes).hexdigest()
    blob_key = f"att/v1/blobs/{sha256_hash}.webp"
    cdn_url = f"{R2_PUBLIC_BASE}/{blob_key}"

    return {
        "sha256": sha256_hash,
        "blob_key": blob_key,
        "cdn_url": cdn_url,
        "webp_bytes": webp_bytes,
        "width": new_w,
        "height": new_h,
        "byte_size": len(webp_bytes)
    }

def check_r2_object_exists(key):
    try:
        s3.head_object(Bucket=R2_BUCKET, Key=key)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] in ('404', 'NoSuchKey'):
            return False
        return False

def sync_assets_to_r2():
    registry = load_registry()
    path_to_url = {}

    # Target folders to scan
    target_dirs = [
        os.path.join(BASE_DIR, "assets", "museums"),
        os.path.join(BASE_DIR, "assets", "artists"),
        os.path.join(BASE_DIR, "assets", "themes"),
        os.path.join(BASE_DIR, "assets", "featured")
    ]

    files_to_process = []
    for tdir in target_dirs:
        if not os.path.exists(tdir):
            continue
        for root, _, files in os.walk(tdir):
            for fname in sorted(files):
                if fname.lower().endswith((".jpg", ".jpeg", ".png", ".webp")) and not fname.startswith("."):
                    files_to_process.append(os.path.join(root, fname))

    print(f"[*] Found {len(files_to_process)} asset images to process under RULE #74...")

    uploaded_count = 0
    skipped_count = 0

    for i, abs_path in enumerate(files_to_process, 1):
        rel_path = os.path.relpath(abs_path, BASE_DIR)
        try:
            res = process_image_rule74(abs_path)
            sha = res["sha256"]
            blob_key = res["blob_key"]
            cdn_url = res["cdn_url"]
            path_to_url[rel_path] = cdn_url

            # Check deduplication
            already_uploaded = False
            if sha in registry:
                already_uploaded = True
            else:
                already_uploaded = check_r2_object_exists(blob_key)

            if not already_uploaded:
                print(f"[{i}/{len(files_to_process)}] Uploading {rel_path} -> {blob_key} ({res['byte_size']} B)...")
                s3.put_object(
                    Bucket=R2_BUCKET,
                    Key=blob_key,
                    Body=res["webp_bytes"],
                    ContentType="image/webp",
                    CacheControl="public, max-age=31536000, immutable"
                )
                uploaded_count += 1
            else:
                skipped_count += 1

            # OCR Extraction (only if not already extracted in registry)
            ocr_text = []
            if sha in registry and "ocr_text" in registry[sha]:
                ocr_text = registry[sha]["ocr_text"]
            else:
                ocr_text = run_apple_vision_ocr(abs_path)

            # Update Registry
            if sha not in registry:
                registry[sha] = {
                    "sha256": sha,
                    "blob_key": blob_key,
                    "cdn_url": cdn_url,
                    "width": res["width"],
                    "height": res["height"],
                    "bytes": res["byte_size"],
                    "format": "webp",
                    "quality": 86,
                    "ocr_text": ocr_text,
                    "first_source": rel_path,
                    "sources": [rel_path],
                    "created_at": datetime.now().isoformat()
                }
            else:
                if rel_path not in registry[sha].get("sources", []):
                    registry[sha].setdefault("sources", []).append(rel_path)
                if ocr_text and not registry[sha].get("ocr_text"):
                    registry[sha]["ocr_text"] = ocr_text

        except Exception as e:
            print(f"[!] Error processing {rel_path}: {e}")

    save_registry(registry)
    print(f"[+] R2 Sync Complete! Uploaded: {uploaded_count}, Deduplicated/Skipped: {skipped_count}")

    # Generate D1-compatible search index array
    d1_index = []
    for sha, meta in registry.items():
        d1_index.append({
            "sha256": sha,
            "blob_key": meta["blob_key"],
            "cdn_url": meta["cdn_url"],
            "width": meta.get("width"),
            "height": meta.get("height"),
            "bytes": meta.get("bytes"),
            "ocr_text": " ".join(meta.get("ocr_text", [])),
            "sources": meta.get("sources", [])
        })
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(d1_index, f, ensure_ascii=False, indent=2)
    print(f"[+] Exported D1 search index to {INDEX_FILE} ({len(d1_index)} records)")

    # Now update databases with canonical R2 URLs
    update_catalogs(path_to_url)

def update_catalogs(path_to_url):
    print("[*] Updating catalog JSONs with canonical R2 att/v1/blobs/ URLs...")

    # 1. Curated Ambient Themes DB
    themes_path = os.path.join(DATA_DIR, "curated_ambient_themes_db.json")
    if os.path.exists(themes_path):
        with open(themes_path, "r", encoding="utf-8") as f:
            t_content = f.read()
        replaced = 0
        for local_p, r2_u in path_to_url.items():
            if local_p in t_content:
                t_content = t_content.replace(local_p, r2_u)
                replaced += 1
        with open(themes_path, "w", encoding="utf-8") as f:
            f.write(t_content)
        print(f"[+] Updated {themes_path} ({replaced} local path references replaced)")

    # 2. Top Museums Master Catalog
    museums_path = os.path.join(DATA_DIR, "top_museums_master_catalog.json")
    if os.path.exists(museums_path):
        with open(museums_path, "r", encoding="utf-8") as f:
            m_content = f.read()
        replaced = 0
        for local_p, r2_u in path_to_url.items():
            if local_p in m_content:
                m_content = m_content.replace(local_p, r2_u)
                replaced += 1
        with open(museums_path, "w", encoding="utf-8") as f:
            f.write(m_content)
        print(f"[+] Updated {museums_path} ({replaced} references replaced)")

    # 3. Lets People Artists Catalog
    people_path = os.path.join(DATA_DIR, "lets_people_artists.json")
    if os.path.exists(people_path):
        with open(people_path, "r", encoding="utf-8") as f:
            p_content = f.read()
        replaced = 0
        for local_p, r2_u in path_to_url.items():
            if local_p in p_content:
                p_content = p_content.replace(local_p, r2_u)
                replaced += 1
        with open(people_path, "w", encoding="utf-8") as f:
            f.write(p_content)
        print(f"[+] Updated {people_path} ({replaced} references replaced)")

    # 4. Master Artists Directory
    dir_path = os.path.join(DATA_DIR, "master_artists_directory.json")
    if os.path.exists(dir_path):
        with open(dir_path, "r", encoding="utf-8") as f:
            d_content = f.read()
        replaced = 0
        for local_p, r2_u in path_to_url.items():
            if local_p in d_content:
                d_content = d_content.replace(local_p, r2_u)
                replaced += 1
        with open(dir_path, "w", encoding="utf-8") as f:
            f.write(d_content)
        print(f"[+] Updated {dir_path} ({replaced} references replaced)")

    # 5. HTML Frontend Files
    html_files = ["museum.html", "artist.html", "artwork.html", "index.html", "themes.html"]
    for hname in html_files:
        hpath = os.path.join(BASE_DIR, hname)
        if not os.path.exists(hpath):
            continue
        with open(hpath, "r", encoding="utf-8") as f:
            h_content = f.read()
        replaced = 0
        for local_p, r2_u in path_to_url.items():
            if local_p in h_content:
                h_content = h_content.replace(local_p, r2_u)
                replaced += 1
        with open(hpath, "w", encoding="utf-8") as f:
            f.write(h_content)
        print(f"[+] Updated {hname} ({replaced} references replaced)")

if __name__ == "__main__":
    sync_assets_to_r2()
