#!/usr/bin/env python3
"""
scripts/pipeline_webp_processor.py
디지털 갤러리 7,865점 작품의 [썸네일 + 4K 고화질 원본] 쌍(Pair) 수집 및 WebP 압축 파이프라인
- 썸네일: WebP 변환 (평균 ~12KB) -> GitHub / 로컬 정적 서빙 최적화
- 고화질 원본: WebP 변환 (4K UHD 3840px 유지, 평균 ~1MB / 2K 2048px 선택 가능)
- 동시 멀티스레딩 지원 및 진행률 로깅
"""

import os
import sys
import json
import io
import argparse
import urllib.request
import urllib.parse
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_BASE = os.path.join(BASE_DIR, "assets", "webp")
THUMB_DIR = os.path.join(OUTPUT_BASE, "thumbnails")
UHD_DIR = os.path.join(OUTPUT_BASE, "uhd")

os.makedirs(THUMB_DIR, exist_ok=True)
os.makedirs(UHD_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def download_bytes(url, timeout=15):
    quoted = urllib.parse.quote(url, safe=':/?&=#%')
    req = urllib.request.Request(quoted, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()

def process_single_artwork(art, mode_2k=False):
    uid = art.get("_raw_uid") or art.get("id")
    uhd_url = art.get("image_url")
    thumb_url = art.get("thumbnail_url")
    
    if not uhd_url:
        return (uid, False, "No UHD URL")

    out_uhd_path = os.path.join(UHD_DIR, f"{uid}.webp")
    out_thumb_path = os.path.join(THUMB_DIR, f"{uid}.webp")

    # 1. 썸네일 WebP 처리
    thumb_bytes = 0
    if not os.path.exists(out_thumb_path):
        try:
            t_data = download_bytes(thumb_url) if thumb_url else None
            if t_data:
                im_t = Image.open(io.BytesIO(t_data))
                im_t.save(out_thumb_path, format="WEBP", quality=80, method=4)
                thumb_bytes = os.path.getsize(out_thumb_path)
        except Exception as e:
            pass

    # 2. 고화질 원본 WebP 처리
    uhd_bytes = 0
    if not os.path.exists(out_uhd_path):
        try:
            u_data = download_bytes(uhd_url)
            im_u = Image.open(io.BytesIO(u_data))
            
            # 2K 모드일 경우 리사이징, 아닐 경우 4K 원본 유지
            if mode_2k:
                im_u.thumbnail((2048, 2048), Image.Resampling.LANCZOS)
                
            im_u.save(out_uhd_path, format="WEBP", quality=80, method=4)
            uhd_bytes = os.path.getsize(out_uhd_path)
        except Exception as e:
            return (uid, False, f"UHD error: {e}")

    return (uid, True, f"Thumb: {thumb_bytes/1024:.1f}KB, UHD: {uhd_bytes/1024/1024:.2f}MB")

def main():
    parser = argparse.ArgumentParser(description="썸네일 + 원본 WebP 쌍 수집 및 압축기")
    parser.add_argument("--limit", type=int, default=5, help="테스트할 수집 작품 수 (기본: 5개)")
    parser.add_argument("--all", action="store_true", help="7,865점 전체 실행")
    parser.add_argument("--workers", type=int, default=10, help="동시 작업 쓰레드 수")
    parser.add_argument("--mode-2k", action="store_true", help="4K 대신 웹 최적화 2K(2048px)로 압축 (용량 60%% 추가 절감)")
    args = parser.parse_args()

    db_path = os.path.join(BASE_DIR, "data", "digital_gallery_master_db.json")
    with open(db_path, "r", encoding="utf-8") as f:
        db = json.load(f)

    artworks = db.get("artworks", [])
    if not args.all:
        artworks = artworks[:args.limit]
        print(f"[*] 테스트 모드: {len(artworks)}점 대상 실행")
    else:
        print(f"[*] 전체 모드: {len(artworks)}점 대상 실행")

    print(f"[*] 저장 위치: {OUTPUT_BASE}")
    print(f"[*] 해상도 모드: {'2K(2048px) 압축' if args.mode_2k else '4K(3840px) 마스터 원본'}")

    success = 0
    fail = 0
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(process_single_artwork, a, args.mode_2k): a for a in artworks}
        for f in as_completed(futures):
            uid, ok, msg = f.result()
            if ok:
                success += 1
                print(f"[+] UID {uid} 완료: {msg}")
            else:
                fail += 1
                print(f"[-] UID {uid} 실패: {msg}")

    print(f"\n==========================================")
    print(f"[*] 처리 완료: 성공 {success}개, 실패 {fail}개")
    print(f"==========================================")

if __name__ == "__main__":
    main()
