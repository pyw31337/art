#!/usr/bin/env python3
"""
scripts/vault_master_harvester.py
High-Speed Parallel Masterpiece Harvester (Unified with LETS_DATA_VAULT)
1. Unified Vault Storage: /Volumes/My Passport for Mac/LETS_DATA_VAULT/services/art
2. High-Throughput Concurrent Harvesting (ThreadPoolExecutor 12+ workers)
3. Multi-Museum Pipeline: The Met, Art Institute of Chicago (AIC), Cleveland Museum (CMA)
4. Robust Retry, DLQ, and Real-Time Heartbeat for Watchdog Monitoring
5. Web Service Hybrid Integration (Zero R2 storage cost, immutable remote CDN linking)
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
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image, ImageOps

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DLQ_PROJECT_FILE = os.path.join(DATA_DIR, "harvest_failed_dlq.json")

def find_vault_root():
    """Finds the unified LETS_DATA_VAULT/services/art path across all drives."""
    if "LETSART_VAULT_ROOT" in os.environ and os.path.exists(os.environ["LETSART_VAULT_ROOT"]):
        return os.environ["LETSART_VAULT_ROOT"]

    pointer = os.path.expanduser("~/.letsart_vault_path")
    if os.path.exists(pointer):
        try:
            with open(pointer, "r") as f:
                p = f.read().strip()
                if os.path.exists(p):
                    return p
        except Exception:
            pass

    volumes = Path("/Volumes")
    if volumes.exists():
        for vol in volumes.iterdir():
            cand_unified = vol / "LETS_DATA_VAULT" / "services" / "art"
            if cand_unified.exists() and cand_unified.is_dir():
                return str(cand_unified)
            cand_legacy = vol / "LETSART_MASTER_VAULT"
            if cand_legacy.exists() and cand_legacy.is_dir():
                return str(cand_legacy)

    return "/Volumes/My Passport for Mac/LETS_DATA_VAULT/services/art"

VAULT_ROOT = find_vault_root()
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
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(dlq_list[-500:], f, ensure_ascii=False, indent=2)
        except Exception:
            pass

def robust_urlopen(req, max_retries=3, base_timeout=15):
    for attempt in range(1, max_retries + 1):
        try:
            return urllib.request.urlopen(req, timeout=base_timeout)
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504):
                sleep_time = min(15, (2 ** attempt) + 1)
                time.sleep(sleep_time)
            else:
                raise e
        except Exception as e:
            sleep_time = (2 ** attempt)
            time.sleep(sleep_time)
    raise TimeoutError(f"Request failed after {max_retries} attempts")

def process_and_save_image(img_url, max_dim=2400):
    """Downloads image, converts to RULE #74 WebP, and saves to External Vault."""
    req = urllib.request.Request(img_url, headers=HEADERS)
    with robust_urlopen(req, max_retries=3, base_timeout=25) as resp:
        raw_bytes = resp.read()

    with Image.open(io.BytesIO(raw_bytes)) as im:
        im = ImageOps.exif_transpose(im)
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

    sha256 = hashlib.sha256(webp_bytes).hexdigest()
    vault_file_path = os.path.join(VAULT_BLOBS_DIR, f"{sha256}.webp")
    if not os.path.exists(vault_file_path):
        with open(vault_file_path, "wb") as f:
            f.write(webp_bytes)

    return sha256, len(webp_bytes)

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

def harvest_met_worker(oid):
    """Worker task to process a single Met object."""
    str_id = f"met_{oid}"
    obj_url = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{oid}"
    try:
        oreq = urllib.request.Request(obj_url, headers=HEADERS)
        with robust_urlopen(oreq, max_retries=2, base_timeout=10) as oresp:
            obj = json.load(oresp)

        if not obj.get("isPublicDomain"):
            return None, str_id, "Not Public Domain"

        img_url = obj.get("primaryImage") or obj.get("primaryImageSmall")
        if not img_url:
            return None, str_id, "No Primary Image"

        title = obj.get("title") or "Untitled"
        artist = obj.get("artistDisplayName") or "Unknown Artist"
        year = obj.get("objectDate") or ""
        medium = obj.get("medium") or ""
        dimensions = obj.get("dimensions") or ""
        department = obj.get("department") or "European Paintings"

        blob_sha256, byte_size = process_and_save_image(img_url)

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

        # Save metadata to Vault
        mpath = os.path.join(VAULT_META_DIR, f"{str_id}.json")
        with open(mpath, "w", encoding="utf-8") as mf:
            json.dump(obj, mf, ensure_ascii=False, indent=2)

        return record, str_id, f"OK ({byte_size//1024} KB)"
    except Exception as e:
        log_to_dlq(str_id, obj_url, str(e))
        return None, str_id, f"Error: {e}"

def harvest_the_met_parallel(limit=100, max_workers=10):
    print(f"\n[*] [The Met] Harvesting up to {limit} paintings with {max_workers} parallel threads...")
    cp = load_checkpoint()
    collected_set = set(cp.get("collected_ids", []))

    # Department 11 (European Paintings) + Department 10 (Egyptian Art)
    url = "https://collectionapi.metmuseum.org/public/collection/v1/objects?departmentIds=11"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with robust_urlopen(req, max_retries=3, base_timeout=15) as resp:
            data = json.load(resp)
            object_ids = data.get("objectIDs", [])
    except Exception as e:
        print(f"[-] Failed to fetch The Met object IDs: {e}")
        return []

    pending_ids = [oid for oid in object_ids if f"met_{oid}" not in collected_set][:limit * 3]
    print(f"[+] Found {len(pending_ids)} unharvested candidate IDs from The Met.")

    harvested = []
    success_count = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_id = {executor.submit(harvest_met_worker, oid): oid for oid in pending_ids}
        for future in as_completed(future_to_id):
            record, str_id, msg = future.result()
            collected_set.add(str_id)
            if record:
                harvested.append(record)
                success_count += 1
                print(f"  [Met {success_count}/{limit}] {record['title'][:30]} ({record['artist'][:20]}) -> {msg}")
                update_heartbeat("RUNNING", str_id, len(harvested), 0)
                if success_count >= limit:
                    # Cancel remaining futures
                    executor.shutdown(wait=False, cancel_futures=True)
                    break

    cp["collected_ids"] = list(collected_set)
    cp["total_count"] = len(collected_set)
    save_checkpoint(cp)
    return harvested

def harvest_aic_worker(art):
    """Worker task to process a single AIC artwork."""
    aid = art.get("id")
    str_id = f"aic_{aid}"
    image_id = art.get("image_id")
    if not image_id or not art.get("is_public_domain"):
        return None, str_id, "Skip (No Image or Not Public Domain)"

    img_url = f"https://www.artic.edu/iiif/2/{image_id}/full/1686,/0/default.jpg"
    thumb_url = f"https://www.artic.edu/iiif/2/{image_id}/full/400,/0/default.jpg"
    title = art.get("title") or "Untitled"
    artist = art.get("artist_title") or "Unknown Artist"

    try:
        blob_sha256, byte_size = process_and_save_image(img_url)

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

        mpath = os.path.join(VAULT_META_DIR, f"{str_id}.json")
        with open(mpath, "w", encoding="utf-8") as mf:
            json.dump(art, mf, ensure_ascii=False, indent=2)

        return record, str_id, f"OK ({byte_size//1024} KB)"
    except Exception as e:
        log_to_dlq(str_id, img_url, str(e))
        return None, str_id, f"Error: {e}"

def harvest_aic_parallel(limit=100, max_workers=10):
    print(f"\n[*] [AIC] Harvesting up to {limit} artworks with {max_workers} parallel threads...")
    cp = load_checkpoint()
    collected_set = set(cp.get("collected_ids", []))

    page_size = min(100, limit * 2)
    url = f"https://api.artic.edu/api/v1/artworks?limit={page_size}&fields=id,title,artist_title,date_display,medium_display,dimensions,image_id,is_public_domain,department_title"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with robust_urlopen(req, max_retries=3, base_timeout=15) as resp:
            data = json.load(resp)
            items = data.get("data", [])
    except Exception as e:
        print(f"[-] Failed to fetch AIC list: {e}")
        return []

    pending_arts = [art for art in items if f"aic_{art.get('id')}" not in collected_set][:limit * 2]
    harvested = []
    success_count = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_art = {executor.submit(harvest_aic_worker, art): art for art in pending_arts}
        for future in as_completed(future_to_art):
            record, str_id, msg = future.result()
            collected_set.add(str_id)
            if record:
                harvested.append(record)
                success_count += 1
                print(f"  [AIC {success_count}/{limit}] {record['title'][:30]} ({record['artist'][:20]}) -> {msg}")
                update_heartbeat("RUNNING", str_id, len(harvested), 0)
                if success_count >= limit:
                    executor.shutdown(wait=False, cancel_futures=True)
                    break

    cp["collected_ids"] = list(collected_set)
    cp["total_count"] = len(collected_set)
    save_checkpoint(cp)
    return harvested

def harvest_cma_worker(art):
    """Worker task to process a single Cleveland Museum of Art (CMA) object."""
    cid = art.get("id")
    str_id = f"cma_{cid}"
    images = art.get("images", {})
    web_url = images.get("web", {}).get("url") if images else None
    if not web_url or not art.get("share_license_status") in ("CC0", "Open Access"):
        return None, str_id, "Skip (No Image or Not CC0)"

    title = art.get("title") or "Untitled"
    creators = art.get("creators", [])
    artist = creators[0].get("description", "Unknown Artist") if creators else "Unknown Artist"

    try:
        blob_sha256, byte_size = process_and_save_image(web_url)

        record = {
            "id": str_id,
            "title": title,
            "title_en": title,
            "artist": artist,
            "artist_en": artist,
            "year": art.get("creation_date") or "",
            "medium": art.get("technique") or "",
            "dimensions": art.get("dimensions", {}).get("framed", {}).get("dimensions") or "",
            "museum": "클리블랜드 미술관 (Cleveland Museum of Art)",
            "museum_en": "Cleveland Museum of Art",
            "department": art.get("department") or "European Painting and Sculpture",
            "source": "Cleveland Museum Open Access",
            "remote_image_url": web_url,
            "remote_thumb_url": web_url,
            "vault_blob_sha256": blob_sha256,
            "is_public_domain": True,
            "harvested_at": datetime.now().isoformat()
        }

        mpath = os.path.join(VAULT_META_DIR, f"{str_id}.json")
        with open(mpath, "w", encoding="utf-8") as mf:
            json.dump(art, mf, ensure_ascii=False, indent=2)

        return record, str_id, f"OK ({byte_size//1024} KB)"
    except Exception as e:
        log_to_dlq(str_id, web_url, str(e))
        return None, str_id, f"Error: {e}"

def harvest_cma_parallel(limit=50, max_workers=10):
    print(f"\n[*] [CMA] Harvesting up to {limit} artworks from Cleveland Museum of Art...")
    cp = load_checkpoint()
    collected_set = set(cp.get("collected_ids", []))

    url = f"https://openaccess-api.clevelandart.org/api/artworks/?limit={limit*2}&has_image=1"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with robust_urlopen(req, max_retries=3, base_timeout=15) as resp:
            data = json.load(resp)
            items = data.get("data", [])
    except Exception as e:
        print(f"[-] Failed to fetch CMA list: {e}")
        return []

    pending_arts = [art for art in items if f"cma_{art.get('id')}" not in collected_set][:limit * 2]
    harvested = []
    success_count = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_art = {executor.submit(harvest_cma_worker, art): art for art in pending_arts}
        for future in as_completed(future_to_art):
            record, str_id, msg = future.result()
            collected_set.add(str_id)
            if record:
                harvested.append(record)
                success_count += 1
                print(f"  [CMA {success_count}/{limit}] {record['title'][:30]} ({record['artist'][:20]}) -> {msg}")
                update_heartbeat("RUNNING", str_id, len(harvested), 0)
                if success_count >= limit:
                    executor.shutdown(wait=False, cancel_futures=True)
                    break

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

def run_harvest(met_limit=50, aic_limit=50, cma_limit=50, max_workers=12):
    print("=" * 65)
    print("  LET'S ART — HIGH-SPEED PARALLEL MASTERPIECE HARVESTER")
    print(f"  Unified Vault Target: {VAULT_ROOT}")
    print(f"  Worker Threads      : {max_workers}")
    print("=" * 65)

    update_heartbeat(status="STARTED", current_item="Init")

    all_harvested = []
    t0 = time.time()
    try:
        # 1. The Met
        met_items = harvest_the_met_parallel(limit=met_limit, max_workers=max_workers)
        all_harvested.extend(met_items)

        # 2. AIC
        aic_items = harvest_aic_parallel(limit=aic_limit, max_workers=max_workers)
        all_harvested.extend(aic_items)

        # 3. CMA (Cleveland Museum of Art)
        cma_items = harvest_cma_parallel(limit=cma_limit, max_workers=max_workers)
        all_harvested.extend(cma_items)

        sync_to_web_database(all_harvested)
        update_heartbeat(status="COMPLETED", processed=len(all_harvested))

    except Exception as fatal_e:
        print(f"[!] Critical Error in harvester run: {fatal_e}")
        update_heartbeat(status="ERROR", current_item=str(fatal_e))
        raise fatal_e

    elapsed = time.time() - t0
    vault_blob_count = len([f for f in os.listdir(VAULT_BLOBS_DIR) if not f.startswith(".")]) if os.path.exists(VAULT_BLOBS_DIR) else 0

    print("\n" + "=" * 65)
    print(f"[+] High-Speed Harvest cycle finished successfully in {elapsed:.1f}s!")
    print(f"    - New artworks harvested : {len(all_harvested)}")
    print(f"    - Harvest Speed          : {len(all_harvested) / max(0.1, elapsed/60):.1f} works/min")
    print(f"    - Total WebP blobs in Vault: {vault_blob_count}")
    print(f"    - Destination            : {VAULT_ROOT}/blobs/")
    print("=" * 65)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--met", type=int, default=50, help="Number of Met artworks")
    parser.add_argument("--aic", type=int, default=50, help="Number of AIC artworks")
    parser.add_argument("--cma", type=int, default=50, help="Number of CMA artworks")
    parser.add_argument("--workers", type=int, default=12, help="Concurrency worker threads")
    args = parser.parse_args()
    run_harvest(met_limit=args.met, aic_limit=args.aic, cma_limit=args.cma, max_workers=args.workers)
