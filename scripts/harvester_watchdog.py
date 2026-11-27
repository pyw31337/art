#!/usr/bin/env python3
"""
scripts/harvester_watchdog.py
Automated watchdog, issue monitor, and health supervisor for Let's Art Vault harvesting:
1. Validates external drive mount & true disk space
2. Tracks live heartbeat of harvester processes
3. Detects hangs, frozen network sockets, or silent crashes
4. Inspects Dead-Letter Queue (DLQ) for error containment
5. Publishes Genuine Observability metrics to data/collection_health_pulse.json
"""

import os
import sys
import json
import time
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
PULSE_FILE = os.path.join(DATA_DIR, "collection_health_pulse.json")
DLQ_FILE = os.path.join(DATA_DIR, "harvest_failed_dlq.json")

def find_vault():
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
            candidate = vol / "LETSART_MASTER_VAULT"
            if candidate.exists():
                return str(candidate)
    return "/Volumes/My Passport for Mac/LETS_DATA_VAULT/services/art"

def check_process_running(script_names=("vault_master_harvester.py", "mass_vault_harvester.py")):
    try:
        all_pids = []
        for sname in script_names:
            proc = subprocess.run(["pgrep", "-f", sname], stdout=subprocess.PIPE, text=True)
            pids = [p.strip() for p in proc.stdout.strip().split("\n") if p.strip()]
            all_pids.extend(pids)
        all_pids = sorted(list(set(all_pids)))
        return len(all_pids) > 0, all_pids
    except Exception:
        return False, []

def inspect_and_supervise(auto_revive=False):
    print("=" * 65)
    print("  LET'S ART — HARVESTER WATCHDOG & SUPERVISOR")
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 65)

    vault_path = find_vault()
    is_vault_mounted = vault_path is not None and os.path.exists(vault_path)

    free_gb = 0
    total_blobs = 0
    total_meta = 0

    if is_vault_mounted:
        # Check real disk space
        stat = shutil.disk_usage(vault_path)
        free_gb = round(stat.free / (1024 ** 3), 2)
        total_gb = round(stat.total / (1024 ** 3), 2)
        print(f"[+] External Vault Mounted: {vault_path}")
        print(f"    Available Disk Space  : {free_gb} GB / {total_gb} GB")

        blobs_dir = os.path.join(vault_path, "blobs")
        if os.path.exists(blobs_dir):
            total_blobs = len([f for f in os.listdir(blobs_dir) if not f.startswith(".")])

        meta_dir = os.path.join(vault_path, "metadata")
        if os.path.exists(meta_dir):
            total_meta = len([f for f in os.listdir(meta_dir) if not f.startswith(".")])
    else:
        print("[!] Warning: LETSART_MASTER_VAULT is currently not mounted.")

    # Check Process status
    is_running, pids = check_process_running()
    print(f"[*] Harvester Process Status: {'RUNNING (PID: ' + ', '.join(pids) + ')' if is_running else 'IDLE / STOPPED'}")

    # Inspect Heartbeat
    heartbeat_status = "UNKNOWN"
    last_ping_seconds_ago = None
    if is_vault_mounted:
        hb_file = os.path.join(vault_path, "logs", "harvester_heartbeat.json")
        if os.path.exists(hb_file):
            try:
                with open(hb_file, "r") as f:
                    hb = json.load(f)
                epoch = hb.get("epoch", 0)
                last_ping_seconds_ago = round(time.time() - epoch, 1)
                heartbeat_status = hb.get("status", "UNKNOWN")
                print(f"[+] Heartbeat: status={heartbeat_status}, last ping={last_ping_seconds_ago}s ago (item: {hb.get('current_item')})")
            except Exception as e:
                print(f"[-] Heartbeat read error: {e}")

    # Check Dead Letter Queue (DLQ)
    dlq_count = 0
    if os.path.exists(DLQ_FILE):
        try:
            with open(DLQ_FILE, "r") as f:
                dlq_items = json.load(f)
                dlq_count = len(dlq_items)
        except Exception:
            dlq_count = 0
    print(f"[*] Quarantine Dead-Letter Queue (DLQ) items: {dlq_count}")

    # Detect Issues
    issue_detected = False
    issue_description = ""
    if is_running and last_ping_seconds_ago and last_ping_seconds_ago > 180:
        issue_detected = True
        issue_description = f"Harvester process frozen (no heartbeat update for {last_ping_seconds_ago}s)"
        print(f"\n[ALERT] {issue_description}")
        if auto_revive:
            print("[*] Watchdog Auto-Revive: Terminating stuck PID and restarting...")
            for pid in pids:
                try:
                    os.kill(int(pid), 9)
                except Exception:
                    pass
            subprocess.Popen([sys.executable, os.path.join(BASE_DIR, "scripts", "vault_master_harvester.py"), "--met", "50", "--aic", "50"])

    # Update collection_health_pulse.json with Genuine Observability
    if os.path.exists(PULSE_FILE):
        try:
            with open(PULSE_FILE, "r") as f:
                pulse = json.load(f)
        except Exception:
            pulse = {}

        pulse["last_monitored_at"] = datetime.now().isoformat()
        pulse["vault_storage"] = {
            "is_mounted": is_vault_mounted,
            "vault_path": vault_path,
            "free_space_gb": free_gb,
            "total_blobs_collected": total_blobs,
            "total_metadata_records": total_meta
        }
        pulse["harvester_watchdog"] = {
            "status": "RUNNING" if is_running else ("STALLED" if issue_detected else "IDLE"),
            "is_process_active": is_running,
            "last_heartbeat_status": heartbeat_status,
            "last_ping_seconds_ago": last_ping_seconds_ago,
            "quarantined_dlq_errors": dlq_count,
            "issue_detected": issue_detected,
            "issue_description": issue_description
        }

        with open(PULSE_FILE, "w", encoding="utf-8") as f:
            json.dump(pulse, f, ensure_ascii=False, indent=2)
        print(f"[+] Updated Genuine Observability metrics in {PULSE_FILE}")

    print("=" * 65)

if __name__ == "__main__":
    inspect_and_supervise()
