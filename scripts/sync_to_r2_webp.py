#!/usr/bin/env python3
"""
scripts/sync_to_r2_webp.py
이씨오 디지털 갤러리 7,865점 전 작품 [썸네일 + 4K UHD 원본] 쌍 WebP 압축 및 Cloudflare R2 고속 업로드 파이프라인
- R2 버킷: letsart-masterpieces
- Public URL: https://pub-685f237e5a544431bee558c5b29f3291.r2.dev
- 썸네일: thumbnails/{uid}.webp (image/webp, ~10KB)
- 4K 원본: uhd/{uid}.webp (image/webp, ~0.9MB)
- 체크포인트 파일(data/r2_upload_checkpoint.json)로 중단 시 언제든 이어서 재개 가능
"""

import os
import sys
import json
import io
import time
import argparse
import urllib.request
import urllib.parse
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed
import boto3
from botocore.config import Config

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
CHECKPOINT_PATH = os.path.join(DATA_DIR, "r2_upload_checkpoint.json")

R2_ENDPOINT = "https://51437a5851eb0715415e7df9e3a4e5c1.r2.cloudflarestorage.com"
R2_ACCESS_KEY = os.environ.get("R2_ACCESS_KEY", "ef93d72d5115e5018cfd7a1cf5980eae")
R2_SECRET_KEY = os.environ.get("R2_SECRET_KEY", "8b2947b1ea954f748a328f502e1043f9e68a4a3d6dbb6f5e670e23d0fcb92552")
R2_BUCKET = "letsart-masterpieces"
R2_PUBLIC_BASE = "https://pub-685f237e5a544431bee558c5b29f3291.r2.dev"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=R2_ENDPOINT,
        aws_access_key_id=R2_ACCESS_KEY,
        aws_secret_access_key=R2_SECRET_KEY,
        region_name="auto",
        config=Config(retries={"max_attempts": 5, "mode": "standard"})
    )

def download_bytes(url, timeout=20, retries=3):
    quoted = urllib.parse.quote(url, safe=':/?&=#%')
    for attempt in range(retries):
        try:
            req = urllib.request.Request(quoted, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if resp.status == 200:
                    return resp.read()
        except Exception:
            time.sleep(0.5 * (attempt + 1))
    return None

def process_and_upload(art, s3_client, mode_2k=False):
    uid = art.get("_raw_uid") or art.get("id")
    uhd_url = art.get("image_url")
    thumb_url = art.get("thumbnail_url")
    
    if not uhd_url:
        return (uid, False, "No URL")

    thumb_key = f"thumbnails/{uid}.webp"
    uhd_key = f"uhd/{uid}.webp"

    try:
        # 1. 썸네일 WebP 변환 및 R2 업로드
        t_data = download_bytes(thumb_url) if thumb_url else None
        if t_data:
            im_t = Image.open(io.BytesIO(t_data))
            out_t = io.BytesIO()
            im_t.save(out_t, format="WEBP", quality=80, method=4)
            s3_client.put_object(
                Bucket=R2_BUCKET,
                Key=thumb_key,
                Body=out_t.getvalue(),
                ContentType="image/webp",
                CacheControl="public, max-age=31536000, immutable"
            )

        # 2. 4K 고화질 원본 WebP 변환 및 R2 업로드
        u_data = download_bytes(uhd_url)
        if not u_data:
            return (uid, False, "UHD download failed")

        im_u = Image.open(io.BytesIO(u_data))
        if mode_2k:
            im_u.thumbnail((2048, 2048), Image.Resampling.LANCZOS)

        out_u = io.BytesIO()
        im_u.save(out_u, format="WEBP", quality=80, method=4)
        u_bytes = out_u.tell()

        s3_client.put_object(
            Bucket=R2_BUCKET,
            Key=uhd_key,
            Body=out_u.getvalue(),
            ContentType="image/webp",
            CacheControl="public, max-age=31536000, immutable"
        )

        return (uid, True, f"UHD: {u_bytes/1024/1024:.2f}MB")
    except Exception as e:
        return (uid, False, str(e))

def update_db_urls(completed_uids):
    print(f"[*] 데이터베이스 URL을 R2 CDN 주소로 갱신 중 ({len(completed_uids)}점 대상)...")
    completed_set = set(str(u) for u in completed_uids)

    # 1. digital_gallery_master_db.json 갱신
    dg_path = os.path.join(DATA_DIR, "digital_gallery_master_db.json")
    if os.path.exists(dg_path):
        with open(dg_path, "r", encoding="utf-8") as f:
            dg = json.load(f)
        for art in dg.get("artworks", []):
            raw_uid = str(art.get("_raw_uid") or art.get("id"))
            if raw_uid in completed_set:
                art["thumbnail_url"] = f"{R2_PUBLIC_BASE}/thumbnails/{raw_uid}.webp"
                art["image_url"] = f"{R2_PUBLIC_BASE}/uhd/{raw_uid}.webp"
        with open(dg_path, "w", encoding="utf-8") as f:
            json.dump(dg, f, ensure_ascii=False, indent=2)

    # 2. art_paintings_master_db.json 갱신
    ap_path = os.path.join(DATA_DIR, "art_paintings_master_db.json")
    if os.path.exists(ap_path):
        with open(ap_path, "r", encoding="utf-8") as f:
            ap = json.load(f)
        for art in ap.get("featured_masterpieces", []):
            raw_uid = str(art.get("_raw_uid") or art.get("id", "").replace("art_eco_", ""))
            if raw_uid in completed_set:
                art["thumbnail_url"] = f"{R2_PUBLIC_BASE}/thumbnails/{raw_uid}.webp"
                art["image_url"] = f"{R2_PUBLIC_BASE}/uhd/{raw_uid}.webp"
        with open(ap_path, "w", encoding="utf-8") as f:
            json.dump(ap, f, ensure_ascii=False, indent=2)

    print("[+] 데이터베이스 URL R2 전환 완료.")

def main():
    parser = argparse.ArgumentParser(description="디지털 갤러리 R2 WebP 업로더")
    parser.add_argument("--limit", type=int, default=10, help="테스트할 작품 수")
    parser.add_argument("--all", action="store_true", help="전체 7,865점 실행")
    parser.add_argument("--workers", type=int, default=15, help="동시 업로드 쓰레드 수")
    parser.add_argument("--mode-2k", action="store_true", help="4K 대신 2K(2048px) 압축 (용량 60%% 추가 절감)")
    args = parser.parse_args()

    db_path = os.path.join(DATA_DIR, "digital_gallery_master_db.json")
    with open(db_path, "r", encoding="utf-8") as f:
        db = json.load(f)

    artworks = db.get("artworks", [])
    
    # 체크포인트 로드
    checkpoint = {}
    if os.path.exists(CHECKPOINT_PATH):
        try:
            with open(CHECKPOINT_PATH, "r", encoding="utf-8") as f:
                checkpoint = json.load(f)
        except Exception:
            checkpoint = {}

    completed_uids = set(checkpoint.keys())
    print(f"[*] 기존 완료된 업로드: {len(completed_uids)}점")

    # 미완료 항목 필터링
    pending = [a for a in artworks if str(a.get("_raw_uid") or a.get("id")) not in completed_uids]
    if not args.all:
        pending = pending[:args.limit]

    print(f"[*] 이번 실행 대상: {len(pending)}점 (동시 쓰레드: {args.workers})")
    print(f"[*] R2 버킷: {R2_BUCKET} -> {R2_PUBLIC_BASE}")

    if not pending:
        print("[+] 모든 작품이 이미 업로드 완료되었습니다!")
        update_db_urls(list(checkpoint.keys()))
        return

    s3 = get_s3_client()
    start_time = time.time()
    success = 0
    fail = 0

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(process_and_upload, a, s3, args.mode_2k): a for a in pending}
        for f in as_completed(futures):
            uid, ok, msg = f.result()
            str_uid = str(uid)
            if ok:
                success += 1
                checkpoint[str_uid] = True
                print(f"[+] [{success}/{len(pending)}] UID {uid} 성공: {msg}")
                # 50개마다 체크포인트 저장
                if success % 50 == 0:
                    with open(CHECKPOINT_PATH, "w", encoding="utf-8") as cp_file:
                        json.dump(checkpoint, cp_file)
            else:
                fail += 1
                print(f"[-] UID {uid} 실패: {msg}")

    # 최종 체크포인트 저장
    with open(CHECKPOINT_PATH, "w", encoding="utf-8") as cp_file:
        json.dump(checkpoint, cp_file)

    # DB URL 갱신
    update_db_urls(list(checkpoint.keys()))

    elapsed = time.time() - start_time
    print(f"\n==========================================")
    print(f"[*] 전체 프로세스 완료: 신규 완료 {success}개, 실패 {fail}개")
    print(f"[*] 총 누적 완료: {len(checkpoint)}점 / 소요시간: {elapsed:.2f}초")
    print(f"==========================================")

if __name__ == "__main__":
    main()
