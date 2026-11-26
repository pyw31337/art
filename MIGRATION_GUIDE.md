# 📦 맥미니(M2) → 집 아이맥(M1) 완벽 자료 이관 가이드

이 문서는 회사 맥미니(M2)에서 수집·보관된 명작 마스터 아카이브(`LETSART_MASTER_VAULT`)와 렛츠아트 프로젝트 전체를 12월에 집 아이맥(M1)으로 1바이트의 손실 없이 원클릭으로 이전하는 공식 표준 절차서입니다.

---

## 1. 이관 구조 및 원리

- **원천 미디어(대용량 WebP / 메타데이터)**: 외장하드에만 100% 저장 (`LETSART_MASTER_VAULT`)
- **프로젝트 코드 및 경량 DB**: GitHub 메인 브랜치(`pyw31337/art`)로 실시간 클라우드 동기화
- **경로 자동 감지(Path-Agnostic)**: 집 아이맥에서 외장하드 이름이 달라져도(`My Passport for Mac`이 아니어도) 스크립트가 연결된 모든 볼륨을 스캔하여 마스터 볼트를 자동으로 찾아 연결합니다.

---

## 2. 12월 회사 맥미니(M2)에서 할 일 (이전 준비)

개인 외장하드를 회사 맥미니에 연결한 후 다음 2단계만 진행합니다:

### Step 1: 매니페스트(무결성 체크섬) 자동 발행
터미널에서 아래 명령을 실행합니다:
```bash
cd ~/Developer/art
python3 scripts/prepare_migration_manifest.py
```
> 외장하드의 `LETSART_MASTER_VAULT/vault_manifest.json`에 전체 파일 수, SHA-256 해시, 체크섬이 자동 기록됩니다.

### Step 2: 외장하드로 폴더 복사
회사 외장하드에 있는 `LETSART_MASTER_VAULT` 폴더 전체를 개인 외장하드로 그대로 복사(드래그 앤 드롭 또는 rsync)합니다:
```bash
# 터미널 복사 예시 (경로명에 맞게 조정)
cp -R "/Volumes/My Passport for Mac/LETSART_MASTER_VAULT" "/Volumes/[개인외장하드명]/"
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
- `~/.letsart_vault_path` 환경 포인터를 자동 등록하여 이후 모든 수집 및 분석 스크립트가 해당 외장하드를 바라보도록 설정합니다.

---

## 4. 이후 작업 재개
집 아이맥에서도 기존과 동일하게 수집 스크립트나 일일 파이프라인을 그대로 실행하시면 됩니다:
```bash
# 중단된 지점부터 이어서 수집 재개
python3 scripts/vault_master_harvester.py --met 50 --aic 50
```
