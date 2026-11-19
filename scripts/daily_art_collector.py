#!/usr/bin/env python3
"""
scripts/daily_art_collector.py
렛츠아트(Let's Art) 24/7 무인 자동 글로벌 명화, 조각, 동양화, 고전 문학, 현대 미술 & 현대 건축 멀티 뮤지엄 수집 파이프라인
"""
import sys
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from multi_museum_collector import run_multi_museum_ingest

if __name__ == "__main__":
    run_multi_museum_ingest()
