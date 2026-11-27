#!/usr/bin/env python3
"""
scripts/mass_vault_harvester.py
High-Throughput Continuous Mass Harvester for Let's Art Master Vault
- Stores 100% of master WebP blobs in External Vault: /Volumes/My Passport for Mac/LETS_DATA_VAULT/services/art
- RULE #74: Exif auto-orientation, 2400px Lanczos, quality 86% WebP, SHA-256 hash deduplication
- RULE #78: Zero local SSD media consumption
- Multi-Source Stream:
  * The Met: Multi-department public domain stream (Depts 11, 21, 6, 13, 10, 1, 9, 19)
  * Art Institute of Chicago (AIC): Paginated IIIF stream (pages 1 to 1000+)
  * Cleveland Museum of Art (CMA): Skip-paginated CC0 stream (skip 0 to 40,000+)
- High-Concurrency: ThreadPoolExecutor with 16-24 worker threads
- Fault-Tolerant: Continuous state checkpoints, live heartbeat, DLQ error logging, auto-flushing
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
FEDERATED_WEB_DB = os.path.join(DATA_DIR, "federated_open_masterpieces.json")

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

for d in [VAULT_BLOBS_DIR, VAULT_META_DIR, VAULT_CHECKPOINTS_DIR, VAULT_LOGS_DIR]:
    os.makedirs(d, exist_ok=True)

CHECKPOINT_FILE = os.path.join(VAULT_CHECKPOINTS_DIR, "harvest_checkpoint.json")
MASS_STATE_FILE = os.path.join(VAULT_CHECKPOINTS_DIR, "mass_harvest_state.json")
HEARTBEAT_FILE = os.path.join(VAULT_LOGS_DIR, "harvester_heartbeat.json")
DLQ_VAULT_FILE = os.path.join(VAULT_LOGS_DIR, "harvest_failed_dlq.json")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'AIC-User-Agent': 'LetsArt/1.0 (pyw31337@gmail.com)'
}

def update_heartbeat(status="RUNNING", current_item="", session_processed=0, session_errors=0, speed=0.0):
    try:
        blobs_count = len([f for f in os.listdir(VAULT_BLOBS_DIR) if not f.startswith(".")]) if os.path.exists(VAULT_BLOBS_DIR) else 0
        hb = {
            "timestamp": datetime.now().isoformat(),
            "epoch": time.time(),
            "pid": os.getpid(),
            "status": status,
            "current_item": current_item,
            "session_processed": session_processed,
            "session_errors": session_errors,
            "speed_per_min": round(speed, 1),
            "vault_root": VAULT_ROOT,
            "total_vault_blobs": blobs_count
        }
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
        try:
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
        except Exception:
            pass

def robust_urlopen(req, max_retries=3, base_timeout=20):
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
    """Downloads image, converts to RULE #74 WebP, and saves directly to External Vault."""
    req = urllib.request.Request(img_url, headers=HEADERS)
    with robust_urlopen(req, max_retries=3, base_timeout=30) as resp:
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
            pass
    return {"collected_ids": [], "total_count": 0}

def save_checkpoint(cp):
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump(cp, f, ensure_ascii=False, indent=2)

def load_mass_state():
    default_state = {
        "aic_current_page": 1,
        "cma_current_skip": 0,
        "met_dept_index": 0,
        "met_depts": [11, 21, 6, 13, 10, 1, 9, 19],
        "met_dept_offsets": {}
    }
    if os.path.exists(MASS_STATE_FILE):
        try:
            with open(MASS_STATE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
                for k, v in default_state.items():
                    if k not in state:
                        state[k] = v
                return state
        except Exception:
            pass
    return default_state

def save_mass_state(state):
    with open(MASS_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def sync_batch_to_web_database(records_batch):
    if not records_batch:
        return 0
    existing = []
    if os.path.exists(FEDERATED_WEB_DB):
        try:
            with open(FEDERATED_WEB_DB, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except Exception:
            existing = []

    existing_ids = {item["id"] for item in existing}
    added = 0
    for r in records_batch:
        if r["id"] not in existing_ids:
            existing.append(r)
            existing_ids.add(r["id"])
            added += 1

    if added > 0:
        with open(FEDERATED_WEB_DB, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
    return added

# --- MET WORKER ---
def harvest_met_worker(oid):
    str_id = f"met_{oid}"
    obj_url = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{oid}"
    try:
        oreq = urllib.request.Request(obj_url, headers=HEADERS)
        with robust_urlopen(oreq, max_retries=2, base_timeout=12) as oresp:
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
        department = obj.get("department") or "Open Access Collection"

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

        mpath = os.path.join(VAULT_META_DIR, f"{str_id}.json")
        with open(mpath, "w", encoding="utf-8") as mf:
            json.dump(obj, mf, ensure_ascii=False, indent=2)

        return record, str_id, f"OK ({byte_size//1024} KB)"
    except Exception as e:
        log_to_dlq(str_id, obj_url, str(e))
        return None, str_id, f"Error: {e}"

# --- AIC WORKER ---
def harvest_aic_worker(art):
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

# --- CMA WORKER ---
def harvest_cma_worker(art):
    cid = art.get("id")
    str_id = f"cma_{cid}"
    images = art.get("images", {})
    web_url = images.get("web", {}).get("url") if images else None
    if not web_url or art.get("share_license_status") not in ("CC0", "Open Access"):
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

def run_mass_harvest(target_records=1000, max_workers=20, continuous=False):
    print("=" * 70)
    print("  LET'S ART — MASS VAULT MASTERPIECE HARVESTER (ENTERPRISE)")
    print(f"  Target Artworks   : {'UNLIMITED (Continuous Mode)' if continuous else target_records}")
    print(f"  Concurrency       : {max_workers} parallel workers")
    print(f"  Unified Vault Dest: {VAULT_BLOBS_DIR}")
    print("=" * 70)

    checkpoint = load_checkpoint()
    collected_set = set(checkpoint.get("collected_ids", []))
    mass_state = load_mass_state()

    print(f"[+] Currently collected in checkpoint: {len(collected_set)} artworks")
    print(f"[+] State: AIC page={mass_state['aic_current_page']}, CMA skip={mass_state['cma_current_skip']}, Met dept idx={mass_state['met_dept_index']}")

    total_harvested_session = 0
    t_start = time.time()
    update_heartbeat(status="RUNNING", current_item="Starting session", session_processed=0)

    while continuous or (total_harvested_session < target_records):
        batch_harvested = []
        target_remaining = 999999 if continuous else (target_records - total_harvested_session)

        # --- STREAM 1: Art Institute of Chicago (AIC) Batch ---
        aic_page = mass_state["aic_current_page"]
        print(f"\n[*] [AIC Stream] Fetching page {aic_page} (limit=100)...")
        aic_url = f"https://api.artic.edu/api/v1/artworks?page={aic_page}&limit=100&fields=id,title,artist_title,date_display,medium_display,dimensions,image_id,is_public_domain,department_title"
        try:
            req = urllib.request.Request(aic_url, headers=HEADERS)
            with robust_urlopen(req, max_retries=3, base_timeout=15) as resp:
                data = json.load(resp)
                aic_items = data.get("data", [])
            mass_state["aic_current_page"] += 1
            save_mass_state(mass_state)

            pending_aic = [item for item in aic_items if f"aic_{item.get('id')}" not in collected_set]
            if pending_aic:
                print(f"[+] Found {len(pending_aic)} unharvested AIC candidates.")
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures = {executor.submit(harvest_aic_worker, item): item for item in pending_aic}
                    for fut in as_completed(futures):
                        rec, str_id, msg = fut.result()
                        collected_set.add(str_id)
                        if rec:
                            batch_harvested.append(rec)
                            total_harvested_session += 1
                            elapsed_min = max(0.1, (time.time() - t_start) / 60)
                            spd = total_harvested_session / elapsed_min
                            update_heartbeat("RUNNING", str_id, total_harvested_session, 0, spd)
                            print(f"  [AIC {total_harvested_session}/{target_records}] {rec['title'][:32]} -> {msg}")
                            if not continuous and total_harvested_session >= target_records:
                                executor.shutdown(wait=False, cancel_futures=True)
                                break
                if batch_harvested:
                    sync_batch_to_web_database(batch_harvested)
                    checkpoint["collected_ids"] = list(collected_set)
                    checkpoint["total_count"] = len(collected_set)
                    save_checkpoint(checkpoint)
                    batch_harvested = []
        except Exception as e:
            print(f"[-] AIC batch error: {e}")

        if not continuous and total_harvested_session >= target_records:
            break

        # --- STREAM 2: Cleveland Museum of Art (CMA) Batch ---
        cma_skip = mass_state["cma_current_skip"]
        print(f"\n[*] [CMA Stream] Fetching skip {cma_skip} (limit=100)...")
        cma_url = f"https://openaccess-api.clevelandart.org/api/artworks/?skip={cma_skip}&limit=100&has_image=1"
        try:
            req = urllib.request.Request(cma_url, headers=HEADERS)
            with robust_urlopen(req, max_retries=3, base_timeout=15) as resp:
                data = json.load(resp)
                cma_items = data.get("data", [])
            mass_state["cma_current_skip"] += 100
            save_mass_state(mass_state)

            pending_cma = [item for item in cma_items if f"cma_{item.get('id')}" not in collected_set]
            if pending_cma:
                print(f"[+] Found {len(pending_cma)} unharvested CMA candidates.")
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures = {executor.submit(harvest_cma_worker, item): item for item in pending_cma}
                    for fut in as_completed(futures):
                        rec, str_id, msg = fut.result()
                        collected_set.add(str_id)
                        if rec:
                            batch_harvested.append(rec)
                            total_harvested_session += 1
                            elapsed_min = max(0.1, (time.time() - t_start) / 60)
                            spd = total_harvested_session / elapsed_min
                            update_heartbeat("RUNNING", str_id, total_harvested_session, 0, spd)
                            print(f"  [CMA {total_harvested_session}/{target_records}] {rec['title'][:32]} -> {msg}")
                            if not continuous and total_harvested_session >= target_records:
                                executor.shutdown(wait=False, cancel_futures=True)
                                break
                if batch_harvested:
                    sync_batch_to_web_database(batch_harvested)
                    checkpoint["collected_ids"] = list(collected_set)
                    checkpoint["total_count"] = len(collected_set)
                    save_checkpoint(checkpoint)
                    batch_harvested = []
        except Exception as e:
            print(f"[-] CMA batch error: {e}")

        if not continuous and total_harvested_session >= target_records:
            break

        # --- STREAM 3: The Met Department Batch ---
        depts = mass_state["met_depts"]
        dept_idx = mass_state["met_dept_index"] % len(depts)
        dept_id = depts[dept_idx]
        mass_state["met_dept_index"] += 1
        save_mass_state(mass_state)

        print(f"\n[*] [The Met Stream] Fetching Department {dept_id}...")
        met_url = f"https://collectionapi.metmuseum.org/public/collection/v1/objects?departmentIds={dept_id}"
        try:
            req = urllib.request.Request(met_url, headers=HEADERS)
            with robust_urlopen(req, max_retries=3, base_timeout=15) as resp:
                data = json.load(resp)
                object_ids = data.get("objectIDs", []) or []

            dept_key = str(dept_id)
            offset = mass_state.get("met_dept_offsets", {}).get(dept_key, 0)
            pending_met = [oid for oid in object_ids[offset:] if f"met_{oid}" not in collected_set][:150]
            if "met_dept_offsets" not in mass_state:
                mass_state["met_dept_offsets"] = {}
            mass_state["met_dept_offsets"][dept_key] = offset + len(pending_met)
            save_mass_state(mass_state)

            if pending_met:
                print(f"[+] Found {len(pending_met)} unharvested Met candidates in Dept {dept_id}.")
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures = {executor.submit(harvest_met_worker, oid): oid for oid in pending_met}
                    for fut in as_completed(futures):
                        rec, str_id, msg = fut.result()
                        collected_set.add(str_id)
                        if rec:
                            batch_harvested.append(rec)
                            total_harvested_session += 1
                            elapsed_min = max(0.1, (time.time() - t_start) / 60)
                            spd = total_harvested_session / elapsed_min
                            update_heartbeat("RUNNING", str_id, total_harvested_session, 0, spd)
                            print(f"  [Met {total_harvested_session}/{target_records}] {rec['title'][:32]} -> {msg}")
                            if not continuous and total_harvested_session >= target_records:
                                executor.shutdown(wait=False, cancel_futures=True)
                                break
                if batch_harvested:
                    sync_batch_to_web_database(batch_harvested)
                    checkpoint["collected_ids"] = list(collected_set)
                    checkpoint["total_count"] = len(collected_set)
                    save_checkpoint(checkpoint)
                    batch_harvested = []
        except Exception as e:
            print(f"[-] The Met batch error: {e}")

        # Sync batch to web database and checkpoint
        if batch_harvested:
            sync_batch_to_web_database(batch_harvested)
            checkpoint["collected_ids"] = list(collected_set)
            checkpoint["total_count"] = len(collected_set)
            save_checkpoint(checkpoint)
            print(f"\n[+] Checkpoint synced: {len(collected_set)} total IDs recorded.")

    # Final sync
    checkpoint["collected_ids"] = list(collected_set)
    checkpoint["total_count"] = len(collected_set)
    save_checkpoint(checkpoint)

    total_time = time.time() - t_start
    final_speed = total_harvested_session / max(0.1, total_time / 60)
    update_heartbeat(status="COMPLETED", session_processed=total_harvested_session, speed=final_speed)

    blobs_count = len([f for f in os.listdir(VAULT_BLOBS_DIR) if not f.startswith(".")]) if os.path.exists(VAULT_BLOBS_DIR) else 0

    print("\n" + "=" * 70)
    print(f"[+] Mass Harvester completed in {total_time:.1f}s ({total_time/60:.1f} min)")
    print(f"    - Session Harvested Works: {total_harvested_session}")
    print(f"    - Throughput Speed       : {final_speed:.1f} works/min")
    print(f"    - Total Vault Blobs Now  : {blobs_count}")
    print("=" * 70)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Let's Art High-Speed Mass Harvester")
    parser.add_argument("--target", type=int, default=1000, help="Target number of artworks to harvest in this run")
    parser.add_argument("--workers", type=int, default=20, help="Number of worker threads (default: 20)")
    parser.add_argument("--continuous", action="store_true", help="Run indefinitely in continuous harvesting mode")
    args = parser.parse_args()

    run_mass_harvest(target_records=args.target, max_workers=args.workers, continuous=args.continuous)
