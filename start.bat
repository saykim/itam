@echo off
chcp 65001 >nul
REM ITAM PoC - 원클릭 시작 스크립트 (Windows)

echo 🚀 ITAM 시스템을 시작합니다...

REM 현재 디렉토리로 이동
cd /d "%~dp0"

REM 기존 서버 종료
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000') do taskkill /PID %%a /F 2>nul

REM 가상환경 확인 및 생성
if not exist "venv" (
    echo 📦 가상환경을 생성합니다...
    python -m venv venv
)

REM 가상환경 활성화
call venv\Scripts\activate.bat

REM 의존성 설치
if not exist "venv\.installed" (
    echo 📦 필요한 패키지를 설치합니다...
    pip install -q flask openpyxl
    echo. > venv\.installed
)

REM DB 초기화 (없으면 생성)
if not exist "itam_prod.db" (
    echo 🗄️ 데이터베이스를 초기화합니다...
    python init_db.py
)

echo.
echo ✅ ITAM 시스템이 시작되었습니다!
echo 🌐 브라우저에서 접속: http://127.0.0.1:5000
echo.
echo 종료하려면 Ctrl+C를 누르세요.
echo ==================================
echo.

REM 서버 시작
python app.py
