#!/bin/bash
# ITAM PoC - 원클릭 시작 스크립트 (Mac/Linux)

echo "🚀 ITAM 시스템을 시작합니다..."

# 현재 디렉토리 확인
cd "$(dirname "$0")"

# 기존 서버 종료
lsof -ti:5000 | xargs kill -9 2>/dev/null

# 가상환경 확인 및 생성
if [ ! -d "venv" ]; then
    echo "📦 가상환경을 생성합니다..."
    python3 -m venv venv
fi

# 가상환경 활성화
source venv/bin/activate

# 의존성 설치
if [ ! -f "venv/.installed" ]; then
    echo "📦 필요한 패키지를 설치합니다..."
    pip install -q flask openpyxl
    touch venv/.installed
fi

# DB 초기화 (없으면 생성)
if [ ! -f "itam_prod.db" ]; then
    echo "🗄️ 데이터베이스를 초기화합니다..."
    python init_db.py
fi

echo ""
echo "✅ ITAM 시스템이 시작되었습니다!"
echo "🌐 브라우저에서 접속: http://127.0.0.1:5000"
echo ""
echo "종료하려면 Ctrl+C를 누르세요."
echo "=================================="
echo ""

# 서버 시작
python app.py
