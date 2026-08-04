#!/bin/bash
# 로컬 소스코드 및 환경변수를 AWS Lightsail 서버로 전송하는 스크립트

SERVER_IP="43.201.190.46"
SSH_KEY_PATH="/Users/1004823/Downloads/LightsailDefaultKey-ap-northeast-2.pem"

echo "=================================================="
echo "🚀 AWS Lightsail 백엔드 마이그레이션 배포 시작"
echo "=================================================="

# 1. SSH 키 권한 설정 및 존재 여부 확인
if [ ! -f "$SSH_KEY_PATH" ]; then
    echo "❌ SSH 키 파일을 다운로드 폴더에서 찾을 수 없습니다."
    echo "   예상 경로: $SSH_KEY_PATH"
    echo "   다운로드 폴더에 'LightsailDefaultKey-ap-northeast-2.pem' 파일이 있는지 확인해 주세요."
    exit 1
fi

chmod 600 "$SSH_KEY_PATH"
echo "✅ SSH Key 권한 설정 완료"

# 2. 서버에 프로젝트 디렉토리 생성
echo "📡 서버 디렉토리 생성 중..."
ssh -i "$SSH_KEY_PATH" -o StrictHostKeyChecking=no ubuntu@$SERVER_IP "mkdir -p ~/kids_library"

# 3. 소스코드 및 .env 업로드 (불필요한 가상환경 및 캐시는 제외)
echo "📦 소스코드 및 환경변수(.env) 업로드 중..."
rsync -avz -e "ssh -i $SSH_KEY_PATH" \
    --exclude='venv' \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='.pytest_cache' \
    --exclude='*.pyc' \
    --exclude='.env' \
    /Users/1004823/Desktop/kids_library/backend \
    ubuntu@$SERVER_IP:~/kids_library/

echo "==========================================================="
echo "🎉 업로드 완료! 서버 파일 존재 여부 검증 중..."
echo "==========================================================="

# 4. 배포 후 핵심 파일 존재 검증 (Post-deploy Verification)
SSH="ssh -i $SSH_KEY_PATH -o StrictHostKeyChecking=no ubuntu@$SERVER_IP"

CRITICAL_FILES=(
    "~/kids_library/backend/core/weekly_schedule.json"
    "~/kids_library/backend/core/taxonomy.py"
    "~/kids_library/backend/main.py"
)

ALL_OK=true
for FILE in "${CRITICAL_FILES[@]}"; do
    if $SSH "test -f $FILE"; then
        echo "  ✅ $FILE"
    else
        echo "  ❌ 누락: $FILE  ← 이 파일이 서버에 없습니다!"
        ALL_OK=false
    fi
done

if [ "$ALL_OK" = false ]; then
    echo ""
    echo "⚠️  누락된 파일이 있습니다. 배포를 다시 실행하거나 scp로 수동 전송 후"
    echo "    sudo systemctl restart fastapi.service 를 실행해주세요."
    exit 1
fi

# 5. 서비스 재시작
echo ""
echo "🔄 fastapi.service 재시작 중..."
$SSH "sudo systemctl restart fastapi.service"
sleep 3

SERVICE_STATUS=$($SSH "sudo systemctl is-active fastapi.service")
if [ "$SERVICE_STATUS" = "active" ]; then
    echo "  ✅ fastapi.service 정상 실행 중"
else
    echo "  ❌ fastapi.service 재시작 실패! 서버 로그를 확인해주세요:"
    echo "     sudo journalctl -u fastapi.service -n 30"
    exit 1
fi

echo ""
echo "=========================================================="
echo "🎉 배포 및 검증 완료!"
echo "   - 서버 IP: $SERVER_IP"
echo "   - 대상 경로: ubuntu@$SERVER_IP:~/kids_library/backend"
echo "=========================================================="
