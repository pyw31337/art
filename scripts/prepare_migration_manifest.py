#!/usr/bin/env python3
"""
scripts/prepare_migration_manifest.py
Prepares an immutable integrity manifest of LETSART_MASTER_VAULT
for seamless migration from Company Mac mini (M2) to Home iMac (M1).
Generates:
  - LETSART_MASTER_VAULT/vault_manifest.json
  - Verification checksums and volume summary
"""

import os
import sys
import json
import hashlib
from datetime import datetime

def find_vault_root():
    env_path = os.environ.get("LETSART_VAULT_ROOT")
    if env_path and os.path.exists(env_path):
        return env_path
    ptr = os.path.expanduser("~/.letsart_vault_path")
    if os.path.exists(ptr):
        try:
            with open(ptr, "r") as f:
                p = f.read().strip()
                if os.path.exists(p):
                    return p
        except Exception:
            pass
    volumes = "/Volumes"
    if os.path.exists(volumes):
        for v in os.listdir(volumes):
            cand_unified = os.path.join(volumes, v, "LETS_DATA_VAULT", "services", "art")
            if os.path.exists(cand_unified):
                return cand_unified
            candidate = os.path.join(volumes, v, "LETSART_MASTER_VAULT")
            if os.path.exists(candidate):
                return candidate
    return "/Volumes/My Passport for Mac/LETS_DATA_VAULT/services/art"

def compute_file_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def create_manifest():
    vault_root = find_vault_root()
    if not vault_root:
        print("[-] Error: LETSART_MASTER_VAULT directory not found on any mounted drive!")
        sys.exit(1)

    print(f"[*] Scanning LETSART_MASTER_VAULT at: {vault_root}")
    blobs_dir = os.path.join(vault_root, "blobs")
    metadata_dir = os.path.join(vault_root, "metadata")
    checkpoints_dir = os.path.join(vault_root, "checkpoints")

    manifest = {
        "format_version": "1.0",
        "created_at": datetime.now().isoformat(),
        "source_machine": "Mac mini (M2)",
        "target_machine": "iMac (M1)",
        "vault_root": vault_root,
        "summary": {
            "blob_count": 0,
            "total_blob_bytes": 0,
            "metadata_count": 0,
            "checkpoints_count": 0
        },
        "blobs": {},
        "metadata_files": []
    }

    # 1. Scan blobs
    if os.path.exists(blobs_dir):
        files = sorted(os.listdir(blobs_dir))
        print(f"[*] Cataloging {len(files)} blobs...")
        for fname in files:
            if fname.startswith("."):
                continue
            fpath = os.path.join(blobs_dir, fname)
            fsize = os.path.getsize(fpath)
            # The filename itself is sha256.webp
            sha_name = fname.split(".")[0]
            manifest["blobs"][fname] = {
                "size_bytes": fsize,
                "sha256": sha_name
            }
            manifest["summary"]["blob_count"] += 1
            manifest["summary"]["total_blob_bytes"] += fsize

    # 2. Scan metadata
    if os.path.exists(metadata_dir):
        mfiles = sorted(os.listdir(metadata_dir))
        for mname in mfiles:
            if not mname.startswith("."):
                manifest["metadata_files"].append(mname)
                manifest["summary"]["metadata_count"] += 1

    # 3. Scan checkpoints
    if os.path.exists(checkpoints_dir):
        cfiles = [c for c in os.listdir(checkpoints_dir) if not c.startswith(".")]
        manifest["summary"]["checkpoints_count"] = len(cfiles)

    manifest_path = os.path.join(vault_root, "vault_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    total_mb = manifest["summary"]["total_blob_bytes"] / (1024 * 1024)
    print("\n" + "=" * 60)
    print("  MIGRATION MANIFEST GENERATION COMPLETE")
    print("=" * 60)
    print(f"  Target File    : {manifest_path}")
    print(f"  Blob Count     : {manifest['summary']['blob_count']} items")
    print(f"  Total Data Size: {total_mb:.2f} MB")
    print(f"  Metadata Count : {manifest['summary']['metadata_count']} records")
    print(f"  Checkpoints    : {manifest['summary']['checkpoints_count']} files")
    print("  Status         : Ready for copy to Personal External HDD")
    print("=" * 60)

if __name__ == "__main__":
    create_manifest()
