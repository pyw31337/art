# 📦 맥미니(M2) → 집 아이맥(M1) 완벽 자료 이관 가이드

이 문서는 회사 맥미니(M2)에서 수집·보관된 마스터 볼트(`LETS_DATA_VAULT/services/art`)와 렛츠아트 프로젝트 전체를 12월에 집 아이맥(M1)으로 1바이트의 손실 없이 원클릭으로 이전하는 공식 표준 절차서입니다.

---

## 1. 이관 구조 및 원리

- **통합 외장하드 단일 마스터 볼트**: 모든 데이터는 `/Volumes/My Passport for Mac/LETS_DATA_VAULT` 단일 루트 산하에 통합 관리됩니다.
  - `services/art/blobs/`: RULE #74 WebP 2400px 원화 블롭 (`<sha256>.webp`)
  - `services/art/metadata/`: 각 미술관 원본 JSON 레코드
  - `services/art/checkpoints/`: 수집 멱등성 체크포인트
  - `services/art/logs/`: 워치독 하트비트 & DLQ
  - `services/art/vault_manifest.json`: 파일별 SHA-256 무결성 매니페스트
- **프로젝트 코드 및 경량 DB**: GitHub 메인 브랜치(`pyw31337/art`)로 실시간 클라우드 동기화
- **경로 자동 감지(Path-Agnostic)**: 집 아이맥에서 외장하드 이름이 달라져도 스크립트가 `LETS_DATA_VAULT`를 자동 탐색하여 연결합니다.

---

## 2. 12월 회사 맥미니(M2)에서 할 일 (이전 준비)

개인 외장하드를 회사 맥미니에 연결한 후 다음 2단계만 진행합니다:

### Step 1: 매니페스트(무결성 체크섬) 자동 발행
터미널에서 아래 명령을 실행합니다:
```bash
cd ~/Developer/art
python3 scripts/prepare_migration_manifest.py
```
> `LETS_DATA_VAULT/services/art/vault_manifest.json`에 전체 파일 수, SHA-256 해시, 체크섬이 자동 기록됩니다.

### Step 2: 외장하드로 폴더 복사
회사 외장하드의 `LETS_DATA_VAULT` 폴더 전체를 개인 외장하드로 그대로 복사(드래그 앤 드롭 또는 rsync)합니다:
```bash
# LETS_DATA_VAULT 폴더 하나만 복사하면 아트뿐 아니라 전체 에코시스템이 100% 동시 이전됩니다
cp -R "/Volumes/My Passport for Mac/LETS_DATA_VAULT" "/Volumes/[개인외장하드명]/"
```

---

## 3. 집 아이맥(M1)에서 할 일 (복원 및 연결)

집 아이맥에 개인 외장하드를 연결한 후 다음 2단계만 진행하면 모든 준비가 끝납니다:

### Step 1: 깃허브 코드 클론 (최초 1회)
```bash
git clone https://github.com/pyw31337/art.git ~/Developer/art
cd ~/Developer/art
```

### Step 2: 자동 마운트 및 100% 무결성 검증
```bash
python3 scripts/verify_and_mount_on_imac.py
```
- 연결된 모든 외장하드를 자동 탐색하여 마스터 볼트를 찾습니다.
- SHA-256 비트 무결성을 자동 검사하여 손상된 파일이 없는지 확인합니다.
- `~/.letsart_vault_path` 환경 포인터를 자동 등록하여 작업 준비를 완료합니다.

---

## 4. 이후 작업 재개
집 아이맥에서도 기존과 동일하게 수집 스크립트나 일일 파이프라인을 그대로 실행하시면 됩니다:
```bash
# 고속 병렬 수집 재개 (The Met + AIC + CMA)
python3 scripts/vault_master_harvester.py --met 100 --aic 100 --cma 100 --workers 12
```
