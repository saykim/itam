# ITAM - IT 자산관리 시스템

---

## 📥 설치 가이드 (How to Install)

### 시스템 요구사항

| 항목 | 최소 요구사항 |
|------|--------------|
| **OS** | Windows 10+, macOS 10.15+, Linux (Ubuntu 20.04+) |
| **Python** | 3.9 이상 |
| **메모리** | 512MB 이상 |
| **디스크** | 100MB 이상 |
| **브라우저** | Chrome, Firefox, Safari, Edge (최신 버전) |

### Step 1: 프로젝트 다운로드

```bash
# Git으로 클론 (GitHub 배포 시)
git clone https://github.com/your-org/IT_asset.git
cd IT_asset

# 또는 ZIP 파일 다운로드 후 압축 해제
unzip IT_asset.zip
cd IT_asset
```

### Step 2: Python 가상환경 생성

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: 의존성 설치

```bash
pip install -r requirements.txt
```

### Step 4: 데이터베이스 초기화

```bash
python init_db.py
```

> 💡 샘플 데이터가 포함된 `itam.db` 파일이 생성됩니다.

### Step 5: 서버 실행

```bash
python app.py
```

### Step 6: 접속 확인

브라우저에서 **http://127.0.0.1:5000** 접속

---

## 🚢 배포 옵션

### 옵션 1: 로컬 개발 서버 (기본)

```bash
python app.py
```
- 테스트/개발용
- 단일 사용자 권장

### 옵션 2: Gunicorn (리눅스 프로덕션)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```
- 다중 워커, 동시 접속 지원
- Nginx 리버스 프록시와 함께 사용 권장

### 옵션 3: Docker (컨테이너)

```dockerfile
# Dockerfile 예시
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
```

```bash
docker build -t itam .
docker run -p 5000:5000 itam
```

### 옵션 4: 클라우드 배포

| 플랫폼 | 설명 |
|--------|------|
| **Render** | 무료 티어, 자동 배포 |
| **Railway** | 간편 설정, PostgreSQL 연동 가능 |
| **AWS EC2** | 완전한 제어권, 확장성 |
| **Heroku** | 간편 배포 (유료) |

---

## 📁 프로젝트 구조

```
IT_asset/
├── app.py                # Flask API 서버 (메인 백엔드)
├── init_db.py            # 데이터베이스 초기화 스크립트
├── import_handler.py     # Excel/CSV Import 기능
├── notification_checker.py # 알림 체크 로직
├── requirements.txt      # Python 의존성
├── itam.db               # SQLite 데이터베이스
├── templates/
│   └── index.html        # 프론트엔드 (SPA)
└── venv/                 # Python 가상환경
```

---

## 🚀 실행 방법

### 1. 환경 설정

```bash
# 프로젝트 디렉토리 이동
cd /Users/kimsy/webapp/IT_asset

# 가상환경 활성화
source venv/bin/activate

# 의존성 설치 (최초 1회)
pip install -r requirements.txt
```

### 2. 데이터베이스 초기화 (최초 1회)

```bash
python init_db.py
```

### 3. 서버 실행

```bash
python app.py
```

### 4. 접속

브라우저에서 `http://127.0.0.1:5000` 접속

---

## 🛠 기술 스택

| 영역 | 기술 |
|------|------|
| **Backend** | Python Flask |
| **Database** | SQLite |
| **Frontend** | Vanilla JS + Chart.js |
| **스타일** | Pure CSS (in `index.html`) |

---

## 📊 주요 기능

### 자산 관리
| 기능 | 설명 | 경로 |
|------|------|------|
| 자산 목록 | HW 자산 조회 (필터링, 검색) | 사이드바 > HW 자산 |
| 자산 등록 | 모달을 통한 신규 자산 등록 | + 자산 등록 버튼 |
| 자산 수정 | 기존 자산 정보 수정 | 수정 버튼 |
| 자산 상세 | 기본정보, 배정이력, 변경이력 탭 | 상세 버튼 |
| 자산 배정/회수 | 사용자에게 자산 할당/회수 | 상세 > 배정/회수 |
| Import/Export | Excel 대량 등록/내보내기 | Import/Export 버튼 |

### 라이선스 관리
| 기능 | 설명 |
|------|------|
| 라이선스 목록 | SW 라이선스 현황 조회 |
| 라이선스 등록 | 신규 라이선스 등록 |
| 라이선스 할당 | 사용자에게 라이선스 배정 |

### 대시보드
| 차트 | 설명 |
|------|------|
| 카테고리별 자산 현황 | 막대 차트 |
| 라이선스 현황 | 사용량 바 |
| 사업장별/부서별 현황 | 도넛/가로바 차트 |
| 사용연한 초과 | 경고 목록 |
| OS EOS 현황 | 지원 만료 목록 |

### 기준정보 관리
- **사업장**: 본사, 공장 등
- **부서**: 조직 구조
- **사용자**: 사원 정보 (일괄회수 기능)
- **카테고리**: 자산 분류 (대/중/소분류)
- **공급업체**: 벤더 정보
- **EOS 정보**: 지원 만료 정보

### 관리 기능
- **실사관리**: 자산 실사 점검
- **알림**: 만료/경고 알림

---

## 🔌 API 구조

### RESTful API 패턴

```
GET     /api/{리소스}           # 목록 조회
POST    /api/{리소스}           # 생성
GET     /api/{리소스}/{id}      # 개별 조회
PUT     /api/{리소스}/{id}      # 수정
DELETE  /api/{리소스}/{id}      # 삭제
```

### 주요 API 엔드포인트

| API | 설명 |
|-----|------|
| `/api/assets` | 자산 CRUD |
| `/api/licenses` | 라이선스 CRUD |
| `/api/users` | 사용자 CRUD |
| `/api/categories` | 카테고리 CRUD |
| `/api/locations` | 사업장 CRUD |
| `/api/departments` | 부서 CRUD |
| `/api/vendors` | 공급업체 CRUD |
| `/api/eos-info` | EOS 정보 CRUD |
| `/api/dashboard/*` | 대시보드 데이터 |

---

## 🗄 데이터베이스 스키마

### 주요 테이블

| 테이블 | 용도 |
|--------|------|
| `AssetMaster` | HW 자산 마스터 |
| `LicenseMaster` | 라이선스 마스터 |
| `AssetCategory` | 자산 분류 |
| `Location` | 사업장 |
| `Department` | 부서 |
| `User` | 사용자 |
| `Vendor` | 공급업체 |
| `EOSInfo` | EOS 정보 |
| `AssetAssignment` | 자산 배정 이력 |
| `LicenseAssignment` | 라이선스 배정 이력 |
| `ChangeHistory` | 변경 이력 |

---

## 💻 개발 방법

### 백엔드 수정 (`app.py`)

```python
@app.route('/api/example', methods=['GET'])
def get_example():
    conn = get_db()
    rows = conn.execute('SELECT * FROM Example').fetchall()
    conn.close()
    return api_response(data=rows_to_list(rows))
```

### 프론트엔드 수정 (`templates/index.html`)

**1. HTML 추가**: 페이지/모달 구조
**2. CSS 추가**: `<style>` 태그 내
**3. JS 추가**: `<script>` 태그 내

```javascript
async function loadExample() {
    const res = await api.get('/api/example');
    if (res.success) {
        // 데이터 렌더링
    }
}
```

### 서버 재시작

코드 수정 후:
```bash
pkill -f "python app.py"
python app.py
```

---

## 📝 코딩 컨벤션

- **API 응답**: `api_response(success, data, message, status)` 형식
- **JS 함수명**: `load{Entity}`, `open{Modal}Modal`, `save{Entity}`
- **CSS 변수**: `:root`에 정의된 `--primary`, `--success` 등 사용
- **모달 ID**: `{entity}Modal` (예: `assetModal`, `categoryModal`)

---

## 🔒 주의사항

1. **DB 백업**: `itam.db` 파일 정기 백업 권장
2. **가상환경**: 항상 `source venv/bin/activate` 후 작업
3. **포트 충돌**: 5000번 포트 사용 중이면 충돌 발생
