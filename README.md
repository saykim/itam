# ITAM - IT Asset Management System (PoC)

## 📌 개요 (Introduction)
ITAM(IT Asset Management) 프로젝트는 기업 내 IT 자산(하드웨어, 소프트웨어, 라이선스)의 전체 수명주기를 효율적으로 관리하기 위한 웹 기반 통합 솔루션입니다. Phase 1(PoC)에서는 SQLite와 Flask를 기반으로 핵심 기능을 구현하여, 자산 현황 파악 및 컴플라이언스 관리의 기틀을 마련했습니다.

## 🎯 주요 기능 (Key Features)
- **통합 자산 관리**: HW(노트북, 데스크탑 등), NW(스위치, AP 등), OT(PLC, HMI 등) 자산의 상세 정보 관리 및 이력(Audit Trail) 추적
- **SW 라이선스 및 키 관리**: 라이선스 유형별(영구/구독) 수량 관리 및 개별 라이선스 키 할당/회수 시스템
- **컴플라이언스 대시보드**: 실시간 자산 현황, 라이선스 가용량, 사용연한/보증 만료 알림 시각화
- **기준 정보 관리**: 사업장(Location), 부서(Department), 사용자(User) 및 자산 카테고리의 체계적 관리
- **데이터 활용**: 엑셀(Excel) 표준 템플릿을 통한 대량 데이터 임포트 및 현재 조회 결과 익스포트 지원
- **알림 센터**: 라이선스 초과 사용, 보증 만료 임박, 사용연한 초과 등 주요 이벤트 자동 알림(인앱)

## 🏗️ 시스템 구조 (Project Structure)
이 프로젝트는 **Python Flask (Backend)**와 **Vanilla JS SPA (Frontend)** 아키텍처를 채택하여 빠르고 현대적인 사용자 경험을 제공합니다.

### 폴더 구조
```
IT_asset/
├── app/                    # (선택 사항) 서비스 로직 분리용 폴더
├── templates/
│   └── index.html          # SPA 프론트엔드 (UI & JS Logic)
├── app.py                  # 메인 서버 (RESTful API & 스키마 관리)
├── init_db.py              # 데이터베이스 초기화 및 초기 데이터 생성
├── import_handler.py       # 엑셀 데이터 처리 엔진
├── notification_checker.py # 백그라운드 알림 점검 로직
├── design-guide-foritam.md # UI/UX 디자인 가이드라인
├── PRD.md                  # 상세 제품 요구사항 문서
└── itam_prod.db            # SQLite 데이터베이스 (운영 데이터)
```

### 기술 스택 (Tech Stack)
- **Server**: Python 3.8+, Flask 3.0+
- **Database**: SQLite3
- **Frontend**: HTML5, Vanilla CSS, Modern JavaScript (ES6+), Chart.js (Data Visualization)
- **Extra**: Openpyxl (Excel Processing)

## 🚀 시작하기 (Quick Start)

### 1. 자동 실행 (권장) ⭐
스크립트 하나로 가상환경 설정, 패키지 설치, DB 초기화, 서버 실행까지 자동으로 진행됩니다.

**Mac/Linux:**
```bash
./start.sh
```

**Windows:**
```cmd
start.bat
```

### 2. 수동 실행 (상세)
```bash
# 1. 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 필수 패키지 설치
pip install -r requirements.txt

# 3. 데이터베이스 초기화 (최초 실행 시 또는 초기화 필요 시)
python init_db.py

# 4. 서버 실행
python app.py
```

## 👤 기여 및 정보 (Metadata)
- **Project Owner**: Say Kim
- **Repository**: [https://github.com/saykim/itam](https://github.com/saykim/itam)
- **Latest Update**: 2026-02-15

---
© 2026 ITAM Project Team. All rights reserved.
