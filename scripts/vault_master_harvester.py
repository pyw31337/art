#!/usr/bin/env python3
"""
scripts/vault_master_harvester.py
Harvests world masterpiece collections following user's Hybrid Architecture:
1. Primary Storage: External HDD (/Volumes/My Passport for Mac/LETSART_MASTER_VAULT)
   - Stores master raw metadata and high-res WebP blobs (RULE #74 compliant).
   - Zero consumption of local Mac disk space (which has only 14GB free).
   - Readily portable for personal HDD migration in December.
2. Web Service Serving:
   - Stable Open Access collections (The Met, AIC, CMA, etc.) are served directly
     from their high-performance official CDNs (Zero Cloudflare R2 storage cost).
   - Only volatile/fragile or critical signature works are selectively mirrored to R2.
"""

import os
import sys
import json
import time
import io
import hashlib
import urllib.request
import urllib.parse
from datetime import datetime
from PIL import Image, ImageOps

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

# External Hard Drive Vault Path
VAULT_ROOT = "/Volumes/My Passport for Mac/LETSART_MASTER_VAULT"
VAULT_BLOBS_DIR = os.path.join(VAULT_ROOT, "blobs")
VAULT_META_DIR = os.path.join(VAULT_ROOT, "metadata")
VAULT_CHECKPOINTS_DIR = os.path.join(VAULT_ROOT, "checkpoints")
VAULT_LOGS_DIR = os.path.join(VAULT_ROOT, "logs")

# Fallback if external HDD is unmounted (safety check)
if not os.path.exists(VAULT_ROOT):
    print(f"[!] Warning: External drive {VAULT_ROOT} not found! Please connect 'My Passport for Mac'.")

CHECKPOINT_FILE = os.path.join(VAULT_CHECKPOINTS_DIR, "harvest_checkpoint.json")
FEDERATED_WEB_DB = os.path.join(DATA_DIR, "federated_open_masterpieces.json")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)',
    'AIC-User-Agent': 'LetsArt/1.0 (pyw31337@gmail.com)'
}

def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"collected_ids": [], "total_count": 0}
    return {"collected_ids": [], "total_count": 0}

def save_checkpoint(cp):
    os.makedirs(VAULT_CHECKPOINTS_DIR, exist_ok=True)
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump(cp, f, ensure_ascii=False, indent=2)

def fetch_met_paintings(limit=100, save_blob_to_vault=True):
    """Fetches highlight public domain European Paintings from The Metropolitan Museum of Art."""
    print(f"\n[*] Harvesting up to {limit} paintings from The Met Open Access API...")
    cp = load_checkpoint()
    collected_set = set(cp.get("collected_ids", []))

    # Fetch European Paintings object IDs
    url = "https://collectionapi.metmuseum.org/public/collection/v1/objects?departmentIds=11"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.load(resp)
            object_ids = data.get("objectIDs", [])
    except Exception as e:
        print(f"[-] Failed to fetch The Met object list: {e}")
        return []

    print(f"[+] The Met Department 11 has {len(object_ids)} object IDs. Filtering new items...")

    harvested = []
    count = 0

    for oid in object_ids:
        if count >= limit:
            break
        str_id = f"met_{oid}"
        if str_id in collected_set:
            continue

        obj_url = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{oid}"
        try:
            oreq = urllib.request.Request(obj_url, headers=HEADERS)
            with urllib.request.urlopen(oreq, timeout=10) as oresp:
                obj = json.load(oresp)

            # Check public domain and valid primary image
            if not obj.get("isPublicDomain"):
                continue
            img_url = obj.get("primaryImage") or obj.get("primaryImageSmall")
            if not img_url:
                continue

            title = obj.get("title") or "Untitled"
            artist = obj.get("artistDisplayName") or "Unknown Artist"
            year = obj.get("objectDate") or ""
            medium = obj.get("medium") or ""
            dimensions = obj.get("dimensions") or ""
            department = obj.get("department") or "European Paintings"

            blob_sha256 = ""
            vault_file_path = ""

            # Download & save to External HDD Vault if requested
            if save_blob_to_vault and os.path.exists(VAULT_BLOBS_DIR):
                try:
                    ireq = urllib.request.Request(img_url, headers=HEADERS)
                    with urllib.request.urlopen(ireq, timeout=20) as iresp:
                        raw_bytes = iresp.read()

                    # Convert to WebP 86% per RULE #74
                    with Image.open(io.BytesIO(raw_bytes)) as im:
                        im = ImageOps.exif_transpose(im)
                        max_dim = 2400
                        w, h = im.size
                        if max(w, h) > max_dim:
                            scale = max_dim / float(max(w, h))
                            im = im.resize((int(round(w * scale)), int(round(h * scale))), Image.Resampling.LANCZOS)
                        if im.mode in ("RGBA", "LA"):
                            im = im.convert("RGBA")
                        else:
                            im = im.convert("RGB")
                        out_buf = io.BytesIO()
                        im.save(out_buf, format="WEBP", quality=86, method=4)
                        webp_bytes = out_buf.getvalue()

                    blob_sha256 = hashlib.sha256(webp_bytes).hexdigest()
                    vault_file_path = os.path.join(VAULT_BLOBS_DIR, f"{blob_sha256}.webp")
                    with open(vault_file_path, "wb") as bf:
                        bf.write(webp_bytes)

                except Exception as img_err:
                    print(f"    [-] Image download failed for {oid}: {img_err}")

            record = {
                "id": str_id,
                "title": title,
                "title_en": title,
                "artist": artist,
                "artist_en": artist,
                "year": year,
                "medium": medium,
                "dimensions": dimensions,
                "museum": "메트로폴리탄 미술관 (The Met, New York)",
                "museum_en": "The Metropolitan Museum of Art",
                "department": department,
                "source": "The Met Open Access",
                "remote_image_url": img_url,
                "remote_thumb_url": obj.get("primaryImageSmall") or img_url,
                "vault_blob_sha256": blob_sha256,
                "is_public_domain": True,
                "harvested_at": datetime.now().isoformat()
            }

            # Save full metadata to Vault
            if os.path.exists(VAULT_META_DIR):
                mpath = os.path.join(VAULT_META_DIR, f"{str_id}.json")
                with open(mpath, "w", encoding="utf-8") as mf:
                    json.dump(obj, mf, ensure_ascii=False, indent=2)

            harvested.append(record)
            collected_set.add(str_id)
            count += 1
            print(f"  [{count}/{limit}] {title} ({artist}) -> Vault SHA: {blob_sha256[:12]}...")

            time.sleep(0.15) # Graceful pacing

        except Exception as e:
            print(f"  [-] Error on {oid}: {e}")
            time.sleep(0.5)

    cp["collected_ids"] = list(collected_set)
    cp["total_count"] = len(collected_set)
    save_checkpoint(cp)

    return harvested

def fetch_aic_masterpieces(limit=50, save_blob_to_vault=True):
    """Fetches public domain artworks from Art Institute of Chicago."""
    print(f"\n[*] Harvesting up to {limit} artworks from Art Institute of Chicago (AIC)...")
    cp = load_checkpoint()
    collected_set = set(cp.get("collected_ids", []))

    url = f"https://api.artic.edu/api/v1/artworks?limit={limit}&fields=id,title,artist_title,date_display,medium_display,dimensions,image_id,is_public_domain,department_title"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.load(resp)
            items = data.get("data", [])
    except Exception as e:
        print(f"[-] Failed to fetch AIC list: {e}")
        return []

    harvested = []
    count = 0
    for art in items:
        if count >= limit:
            break
        aid = art.get("id")
        str_id = f"aic_{aid}"
        if str_id in collected_set:
            continue

        if not art.get("is_public_domain"):
            continue
        image_id = art.get("image_id")
        if not image_id:
            continue

        img_url = f"https://www.artic.edu/iiif/2/{image_id}/full/1686,/0/default.jpg"
        thumb_url = f"https://www.artic.edu/iiif/2/{image_id}/full/400,/0/default.jpg"
        title = art.get("title") or "Untitled"
        artist = art.get("artist_title") or "Unknown Artist"

        blob_sha256 = ""
        if save_blob_to_vault and os.path.exists(VAULT_BLOBS_DIR):
            try:
                ireq = urllib.request.Request(img_url, headers=HEADERS)
                with urllib.request.urlopen(ireq, timeout=20) as iresp:
                    raw_bytes = iresp.read()

                with Image.open(io.BytesIO(raw_bytes)) as im:
                    im = ImageOps.exif_transpose(im)
                    max_dim = 2400
                    w, h = im.size
                    if max(w, h) > max_dim:
                        scale = max_dim / float(max(w, h))
                        im = im.resize((int(round(w * scale)), int(round(h * scale))), Image.Resampling.LANCZOS)
                    if im.mode in ("RGBA", "LA"):
                        im = im.convert("RGBA")
                    else:
                        im = im.convert("RGB")
                    out_buf = io.BytesIO()
                    im.save(out_buf, format="WEBP", quality=86, method=4)
                    webp_bytes = out_buf.getvalue()

                blob_sha256 = hashlib.sha256(webp_bytes).hexdigest()
                vault_file_path = os.path.join(VAULT_BLOBS_DIR, f"{blob_sha256}.webp")
                with open(vault_file_path, "wb") as bf:
                    bf.write(webp_bytes)

            except Exception as img_err:
                print(f"    [-] AIC Image download error: {img_err}")

        record = {
            "id": str_id,
            "title": title,
            "title_en": title,
            "artist": artist,
            "artist_en": artist,
            "year": art.get("date_display") or "",
            "medium": art.get("medium_display") or "",
            "dimensions": art.get("dimensions") or "",
            "museum": "시카고 미술관 (Art Institute of Chicago)",
            "museum_en": "Art Institute of Chicago",
            "department": art.get("department_title") or "Paintings and Sculpture",
            "source": "AIC Open Access IIIF",
            "remote_image_url": img_url,
            "remote_thumb_url": thumb_url,
            "vault_blob_sha256": blob_sha256,
            "is_public_domain": True,
            "harvested_at": datetime.now().isoformat()
        }

        harvested.append(record)
        collected_set.add(str_id)
        count += 1
        print(f"  [{count}/{limit}] {title} ({artist}) -> Vault SHA: {blob_sha256[:12]}...")
        time.sleep(0.15)

    cp["collected_ids"] = list(collected_set)
    cp["total_count"] = len(collected_set)
    save_checkpoint(cp)

    return harvested

def sync_to_web_database(new_records):
    """Updates lightweight web search DB with stable remote CDN links."""
    existing = []
    if os.path.exists(FEDERATED_WEB_DB):
        try:
            with open(FEDERATED_WEB_DB, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except Exception:
            existing = []

    existing_ids = {item["id"] for item in existing}
    added = 0
    for r in new_records:
        if r["id"] not in existing_ids:
            existing.append(r)
            existing_ids.add(r["id"])
            added += 1

    with open(FEDERATED_WEB_DB, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

    print(f"[+] Updated {FEDERATED_WEB_DB} (+{added} items, total {len(existing)} open masterpieces)")

def run_harvest(met_limit=25, aic_limit=25):
    print("=" * 65)
    print("  LET'S ART — EXTERNAL VAULT MASTER HARVESTER (HYBRID ARCHITECTURE)")
    print(f"  Vault Target: {VAULT_ROOT}")
    print("=" * 65)

    all_harvested = []
    # 1. Harvest The Met
    met_items = fetch_met_paintings(limit=met_limit, save_blob_to_vault=True)
    all_harvested.extend(met_items)

    # 2. Harvest AIC
    aic_items = fetch_aic_masterpieces(limit=aic_limit, save_blob_to_vault=True)
    all_harvested.extend(aic_items)

    # 3. Sync to lightweight web search DB
    sync_to_web_database(all_harvested)

    # 4. Vault Audit Summary
    vault_blob_count = len(os.listdir(VAULT_BLOBS_DIR)) if os.path.exists(VAULT_BLOBS_DIR) else 0
    print("\n" + "=" * 65)
    print(f"[+] Harvest cycle finished successfully!")
    print(f"    - New artworks harvested: {len(all_harvested)}")
    print(f"    - Total WebP blobs preserved in External HDD Vault: {vault_blob_count}")
    print(f"    - Zero cloud storage cost: Remote CDN images linked directly for web")
    print("=" * 65)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--met", type=int, default=25, help="Number of Met artworks to harvest")
    parser.add_argument("--aic", type=int, default=25, help="Number of AIC artworks to harvest")
    args = parser.parse_args()
    run_harvest(met_limit=args.met, aic_limit=args.aic)
