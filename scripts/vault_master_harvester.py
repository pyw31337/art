#!/usr/bin/env python3
"""
scripts/vault_master_harvester.py
Harvests world masterpiece collections following user's Hybrid Architecture:
1. Dynamic Path-Agnostic Vault Discovery (seamless on M2 Mac mini and M1 iMac)
2. Robust Exponential Backoff Retry & Rate-limit Handling
3. Dead-Letter Queue (DLQ) for non-blocking error containment
4. Live Heartbeat logging for watchdog monitoring
5. External HDD Primary Storage + Zero-cost Web Serving
"""

import os
import sys
import json
import time
import io
import hashlib
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime
from PIL import Image, ImageOps

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DLQ_PROJECT_FILE = os.path.join(DATA_DIR, "harvest_failed_dlq.json")

def find_vault_root():
    """Dynamically finds LETSART_MASTER_VAULT across any connected volume."""
    # 1. Environment variable override
    env_path = os.environ.get("LETSART_VAULT_ROOT")
    if env_path and os.path.exists(env_path):
        return env_path

    # 2. Local config pointer file
    config_pointer = os.path.expanduser("~/.letsart_vault_path")
    if os.path.exists(config_pointer):
        try:
            with open(config_pointer, "r", encoding="utf-8") as f:
                saved_path = f.read().strip()
                if os.path.exists(saved_path):
                    return saved_path
        except Exception:
            pass

    # 3. Scan all mounted /Volumes/
    volumes = "/Volumes"
    if os.path.exists(volumes):
        for v in os.listdir(volumes):
            candidate = os.path.join(volumes, v, "LETSART_MASTER_VAULT")
            if os.path.exists(candidate):
                return candidate

    return None

VAULT_ROOT = find_vault_root() or "/Volumes/My Passport for Mac/LETSART_MASTER_VAULT"
VAULT_BLOBS_DIR = os.path.join(VAULT_ROOT, "blobs")
VAULT_META_DIR = os.path.join(VAULT_ROOT, "metadata")
VAULT_CHECKPOINTS_DIR = os.path.join(VAULT_ROOT, "checkpoints")
VAULT_LOGS_DIR = os.path.join(VAULT_ROOT, "logs")

os.makedirs(VAULT_BLOBS_DIR, exist_ok=True)
os.makedirs(VAULT_META_DIR, exist_ok=True)
os.makedirs(VAULT_CHECKPOINTS_DIR, exist_ok=True)
os.makedirs(VAULT_LOGS_DIR, exist_ok=True)

CHECKPOINT_FILE = os.path.join(VAULT_CHECKPOINTS_DIR, "harvest_checkpoint.json")
HEARTBEAT_FILE = os.path.join(VAULT_LOGS_DIR, "harvester_heartbeat.json")
DLQ_VAULT_FILE = os.path.join(VAULT_LOGS_DIR, "harvest_failed_dlq.json")
FEDERATED_WEB_DB = os.path.join(DATA_DIR, "federated_open_masterpieces.json")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)',
    'AIC-User-Agent': 'LetsArt/1.0 (pyw31337@gmail.com)'
}

def update_heartbeat(status="RUNNING", current_item="", processed=0, errors=0):
    """Writes live heartbeat for the Watchdog daemon."""
    hb = {
        "timestamp": datetime.now().isoformat(),
        "epoch": time.time(),
        "pid": os.getpid(),
        "status": status,
        "current_item": current_item,
        "session_processed": processed,
        "session_errors": errors,
        "vault_root": VAULT_ROOT
    }
    try:
        with open(HEARTBEAT_FILE, "w", encoding="utf-8") as f:
            json.dump(hb, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def log_to_dlq(item_id, source_url, error_msg, raw_info=None):
    """Quarantines permanently failed items to Dead Letter Queue without crashing the harvester."""
    entry = {
        "id": item_id,
        "source_url": source_url,
        "error": str(error_msg),
        "failed_at": datetime.now().isoformat(),
        "raw_info": raw_info
    }
    for filepath in [DLQ_PROJECT_FILE, DLQ_VAULT_FILE]:
        dlq_list = []
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    dlq_list = json.load(f)
            except Exception:
                dlq_list = []
        dlq_list.append(entry)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(dlq_list[-500:], f, ensure_ascii=False, indent=2)
    print(f"    [!] Quarantined to DLQ: {item_id} -> {error_msg}")

def robust_urlopen(req, max_retries=4, base_timeout=15):
    """Performs HTTP request with exponential backoff on transient errors and rate limits."""
    for attempt in range(1, max_retries + 1):
        try:
            return urllib.request.urlopen(req, timeout=base_timeout)
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504):
                sleep_time = (2 ** attempt) + 1
                if e.code == 429:
                    sleep_time = max(sleep_time, 10)
                print(f"    [*] HTTP {e.code} received. Exponential backoff {sleep_time}s (Attempt {attempt}/{max_retries})...")
                time.sleep(sleep_time)
            else:
                raise e
        except (urllib.error.URLError, TimeoutError, ConnectionResetError) as e:
            sleep_time = (2 ** attempt)
            print(f"    [*] Network error: {e}. Retrying in {sleep_time}s (Attempt {attempt}/{max_retries})...")
            time.sleep(sleep_time)

    raise TimeoutError(f"Exhausted all {max_retries} attempts.")

def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"collected_ids": [], "total_count": 0}
    return {"collected_ids": [], "total_count": 0}

def save_checkpoint(cp):
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump(cp, f, ensure_ascii=False, indent=2)

def fetch_met_paintings(limit=50, save_blob_to_vault=True):
    print(f"\n[*] Harvesting up to {limit} paintings from The Met Open Access API...")
    cp = load_checkpoint()
    collected_set = set(cp.get("collected_ids", []))

    url = "https://collectionapi.metmuseum.org/public/collection/v1/objects?departmentIds=11"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with robust_urlopen(req) as resp:
            data = json.load(resp)
            object_ids = data.get("objectIDs", [])
    except Exception as e:
        print(f"[-] Failed to fetch The Met object list: {e}")
        return []

    print(f"[+] The Met European Paintings: {len(object_ids)} IDs available. Filtering...")

    harvested = []
    count = 0
    errors = 0

    for oid in object_ids:
        if count >= limit:
            break
        str_id = f"met_{oid}"
        if str_id in collected_set:
            continue

        update_heartbeat(status="RUNNING", current_item=str_id, processed=count, errors=errors)

        obj_url = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{oid}"
        try:
            oreq = urllib.request.Request(obj_url, headers=HEADERS)
            with robust_urlopen(oreq, max_retries=3, base_timeout=10) as oresp:
                obj = json.load(oresp)

            if not obj.get("isPublicDomain"):
                collected_set.add(str_id)
                continue
            img_url = obj.get("primaryImage") or obj.get("primaryImageSmall")
            if not img_url:
                collected_set.add(str_id)
                continue

            title = obj.get("title") or "Untitled"
            artist = obj.get("artistDisplayName") or "Unknown Artist"
            year = obj.get("objectDate") or ""
            medium = obj.get("medium") or ""
            dimensions = obj.get("dimensions") or ""
            department = obj.get("department") or "European Paintings"

            blob_sha256 = ""
            if save_blob_to_vault and os.path.exists(VAULT_BLOBS_DIR):
                try:
                    ireq = urllib.request.Request(img_url, headers=HEADERS)
                    with robust_urlopen(ireq, max_retries=3, base_timeout=20) as iresp:
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
                    errors += 1
                    log_to_dlq(str_id, img_url, f"Image processing failed: {img_err}")
                    collected_set.add(str_id)
                    continue

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

            if os.path.exists(VAULT_META_DIR):
                mpath = os.path.join(VAULT_META_DIR, f"{str_id}.json")
                with open(mpath, "w", encoding="utf-8") as mf:
                    json.dump(obj, mf, ensure_ascii=False, indent=2)

            harvested.append(record)
            collected_set.add(str_id)
            count += 1
            print(f"  [{count}/{limit}] {title} ({artist}) -> Vault SHA: {blob_sha256[:12]}...")

            time.sleep(0.15) # Gentle pacing

        except Exception as e:
            errors += 1
            log_to_dlq(str_id, obj_url, f"Object fetch failed: {e}")
            collected_set.add(str_id)
            time.sleep(0.5)

    cp["collected_ids"] = list(collected_set)
    cp["total_count"] = len(collected_set)
    save_checkpoint(cp)

    return harvested

def fetch_aic_masterpieces(limit=50, save_blob_to_vault=True):
    print(f"\n[*] Harvesting up to {limit} artworks from Art Institute of Chicago (AIC)...")
    cp = load_checkpoint()
    collected_set = set(cp.get("collected_ids", []))

    url = f"https://api.artic.edu/api/v1/artworks?limit={limit*2}&fields=id,title,artist_title,date_display,medium_display,dimensions,image_id,is_public_domain,department_title"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with robust_urlopen(req) as resp:
            data = json.load(resp)
            items = data.get("data", [])
    except Exception as e:
        print(f"[-] Failed to fetch AIC list: {e}")
        return []

    harvested = []
    count = 0
    errors = 0

    for art in items:
        if count >= limit:
            break
        aid = art.get("id")
        str_id = f"aic_{aid}"
        if str_id in collected_set:
            continue

        update_heartbeat(status="RUNNING", current_item=str_id, processed=count, errors=errors)

        if not art.get("is_public_domain"):
            collected_set.add(str_id)
            continue
        image_id = art.get("image_id")
        if not image_id:
            collected_set.add(str_id)
            continue

        img_url = f"https://www.artic.edu/iiif/2/{image_id}/full/1686,/0/default.jpg"
        thumb_url = f"https://www.artic.edu/iiif/2/{image_id}/full/400,/0/default.jpg"
        title = art.get("title") or "Untitled"
        artist = art.get("artist_title") or "Unknown Artist"

        blob_sha256 = ""
        if save_blob_to_vault and os.path.exists(VAULT_BLOBS_DIR):
            try:
                ireq = urllib.request.Request(img_url, headers=HEADERS)
                with robust_urlopen(ireq, max_retries=3, base_timeout=20) as iresp:
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
                errors += 1
                log_to_dlq(str_id, img_url, f"AIC Image download error: {img_err}")
                collected_set.add(str_id)
                continue

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
    print("  LET'S ART — ROBUST VAULT HARVESTER (WITH DLQ & WATCHDOG)")
    print(f"  Vault Target: {VAULT_ROOT}")
    print("=" * 65)

    update_heartbeat(status="STARTED", current_item="Init")

    all_harvested = []
    try:
        met_items = fetch_met_paintings(limit=met_limit, save_blob_to_vault=True)
        all_harvested.extend(met_items)

        aic_items = fetch_aic_masterpieces(limit=aic_limit, save_blob_to_vault=True)
        all_harvested.extend(aic_items)

        sync_to_web_database(all_harvested)
        update_heartbeat(status="COMPLETED", processed=len(all_harvested))

    except Exception as fatal_e:
        print(f"[!] Critical Error in harvester run: {fatal_e}")
        update_heartbeat(status="ERROR", current_item=str(fatal_e))
        raise fatal_e

    vault_blob_count = len([f for f in os.listdir(VAULT_BLOBS_DIR) if not f.startswith(".")]) if os.path.exists(VAULT_BLOBS_DIR) else 0
    print("\n" + "=" * 65)
    print(f"[+] Harvest cycle finished successfully!")
    print(f"    - New artworks harvested: {len(all_harvested)}")
    print(f"    - Total WebP blobs in External HDD Vault: {vault_blob_count}")
    print("=" * 65)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--met", type=int, default=25, help="Number of Met artworks to harvest")
    parser.add_argument("--aic", type=int, default=25, help="Number of AIC artworks to harvest")
    args = parser.parse_args()
    run_harvest(met_limit=args.met, aic_limit=args.aic)
