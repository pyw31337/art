#!/usr/bin/env python3
"""
scripts/download_uhd_images.py
이씨오 디지털 갤러리 7,865점의 4K UHD(3840px) 마스터 원본 이미지 고속 병렬 다운로더
사용법:
  - 전체 다운로드: python3 scripts/download_uhd_images.py
  - 특정 작가 다운로드: python3 scripts/download_uhd_images.py --artist 1 (반 고흐 341점)
  - 상위 N개 테스트: python3 scripts/download_uhd_images.py --limit 10
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def find_vault_blobs_dir():
    # 1. Environment variable
    env_path = os.environ.get("LETSART_VAULT_ROOT")
    if env_path and os.path.exists(env_path):
        return os.path.join(env_path, "blobs")
    # 2. Pointer file
    ptr = os.path.expanduser("~/.letsart_vault_path")
    if os.path.exists(ptr):
        try:
            with open(ptr, "r") as f:
                p = f.read().strip()
                if os.path.exists(p):
                    return os.path.join(p, "blobs")
        except Exception:
            pass
    # 3. Search /Volumes
    volumes = "/Volumes"
    if os.path.exists(volumes):
        for v in os.listdir(volumes):
            cand = os.path.join(volumes, v, "LETSART_MASTER_VAULT", "blobs")
            if os.path.exists(cand):
                return cand
    return os.path.join(BASE_DIR, "assets", "uhd_images")

IMAGE_DIR = find_vault_blobs_dir()
os.makedirs(IMAGE_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def download_one(art, overwrite=False):
    uid = art.get("_raw_uid") or art.get("id")
    url = art.get("image_url")
    if not url:
        return (uid, False, "No URL")

    # Safe filename: {uid}_{title}.jpg
    raw_fname = os.path.basename(urllib.parse.unquote(url))
    fname = f"{uid}_{raw_fname}"
    # Remove problematic characters for filesystem
    for ch in [":", "/", "\\", "?", "*", "\"", "<", ">", "|"]:
        fname = fname.replace(ch, "_")

    out_path = os.path.join(IMAGE_DIR, fname)
    if not overwrite and os.path.exists(out_path) and os.path.getsize(out_path) > 10000:
        return (uid, True, "Already exists")

    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
            with open(out_path, "wb") as f:
                f.write(data)
            return (uid, True, f"{len(data)/1024/1024:.2f} MB")
    except Exception as e:
        return (uid, False, str(e))

def main():
    parser = argparse.ArgumentParser(description="디지털 갤러리 4K UHD 이미지 다운로더")
    parser.add_argument("--artist", type=int, help="특정 작가 ID (예: 1=반 고흐)")
    parser.add_argument("--limit", type=int, help="최대 다운로드 개수")
    parser.add_argument("--workers", type=int, default=10, help="동시 다운로드 쓰레드 수")
    parser.add_argument("--overwrite", action="store_true", help="기존 파일 덮어쓰기")
    args = parser.parse_args()

    db_path = os.path.join(BASE_DIR, "data", "digital_gallery_master_db.json")
    if not os.path.exists(db_path):
        print("[-] digital_gallery_master_db.json 파일이 없습니다.")
        sys.exit(1)

    with open(db_path, "r", encoding="utf-8") as f:
        db = json.load(f)

    artworks = db.get("artworks", [])
    if args.artist:
        artworks = [a for a in artworks if a.get("_raw_artist_uid") == args.artist]
        print(f"[*] 작가 ID {args.artist}의 작품 {len(artworks)}점 대상")

    if args.limit:
        artworks = artworks[:args.limit]
        print(f"[*] 최대 {args.limit}점 제한 다운로드")

    print(f"[*] 총 {len(artworks)}점 4K UHD 이미지 다운로드 시작 -> {IMAGE_DIR}")

    success = 0
    fail = 0
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(download_one, a, args.overwrite): a for a in artworks}
        for f in as_completed(futures):
            uid, ok, msg = f.result()
            if ok:
                success += 1
            else:
                fail += 1
                print(f"[-] UID {uid} 실패: {msg}")

    print(f"[+] 다운로드 완료: 성공 {success}개, 실패 {fail}개")
    print(f"[+] 저장 위치: {IMAGE_DIR}")

if __name__ == "__main__":
    main()
