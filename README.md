# ITAM - IT Asset Management System (PoC)

## 📌 개요 (Introduction)
ITAM(IT Asset Management) 프로젝트는 기업 내 IT 자산(하드웨어, 소프트웨어, 라이선스)의 전체 수명주기를 효율적으로 관리하기 위한 웹 기반 솔루션입니다. Phase 1(PoC) 단계에서는 SQLite를 기반으로 핵심 기능을 구현하여, 자산 현황 파악 및 컴플라이언스 관리의 기틀을 마련했습니다.

## 🎯 개발 목적 (Why)
- **자산 가시성 확보**: 분산된 IT 자산을 중앙에서 통합 관리하여 불필요한 중복 구매 방지
- **라이선스 컴플라이언스 준수**: SW 라이선스 초과 사용으로 인한 법적 리스크 사전 예방
- **비용 절감**: 유휴 자산(여유, 수리중)의 효율적 재배치 및 유지보수 비용 최적화
- **업무 효율화**: 엑셀 수기 관리의 한계를 극복하고, 자산 이력 자동 추적 및 알림 제공

## 🏗️ 시스템 구조 (Project Structure)
이 프로젝트는 **Python Flask (Backend)**와 **HTML5/JS (Frontend)**, **SQLite (Database)**로 구성된 경량화된 아키텍처를 채택했습니다.

### 폴더 구조
```
IT_asset/
├── app.py                  # 메인 애플리케이션 (Backend API & Server)
├── init_db.py              # 데이터베이스 초기화 및 샘플 데이터 생성
├── itam_prod.db            # SQLite 데이터베이스 파일 (실제 운영 데이터)
├── import_handler.py       # 엑셀 데이터 Import/Export 처리 로직
├── notification_checker.py # 알림 생성 및 배치 작업 처리
├── requirements.txt        # Python 패키지 의존성 목록
├── templates/
│   └── index.html          # SPA(Single Page Application) 프론트엔드 코드
└── README.md               # 프로젝트 매뉴얼
```

### 기술 스택
- **Backend**: Python 3.8+, Flask, SQLite3
- **Frontend**: HTML5, CSS3 (Vanilla), JavaScript (ES6+), Chart.js (시각화)
- **Deployment**: AWS Lightsail (Ubuntu) / Local Host

## 🚀 사용 가이드 (How to Use)

### 1. 사전 준비
- Python 3.8 이상 설치
- (권장) 가상환경(venv) 사용

### 2. 빠른 시작 (원클릭) ⭐
가장 간단한 방법! 스크립트 하나로 자동 설치 및 실행됩니다.

**Mac/Linux:**
```bash
cd IT_asset
./start.sh
```

**Windows:**
```cmd
cd IT_asset
start.bat
```

> 가상환경 생성, 패키지 설치, DB 초기화, 서버 시작이 자동으로 진행됩니다.

### 3. 수동 설치 및 실행 (선택)
```bash
# 1. 프로젝트 폴더로 이동
cd IT_asset

# 2. 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 필수 패키지 설치
pip install -r requirements.txt

# 4. 데이터베이스 초기화 (최초 1회)
python init_db.py
# (주의: 기존 데이터는 초기화됩니다. 실제 운영 시 백업 필수)

# 5. 서버 실행
python app.py
```

### 3. 접속
웹 브라우저에서 `http://127.0.0.1:5000` 주소로 접속합니다.
- **초기 계정**: 별도 로그인 없이 접속 가능 (PoC 단계)

## 👤 개발자 정보 (Contributors)
- **Project Owner**: Say Kim
- **Repository**: [https://github.com/saykim/itam](https://github.com/saykim/itam)

## 📅 최종 업데이트 (Last Updated)
**2026년 2월 8일**
