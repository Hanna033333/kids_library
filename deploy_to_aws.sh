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
    /Users/1004823/Desktop/kids_library/backend \
    ubuntu@$SERVER_IP:~/kids_library/

echo "=================================================="
echo "🎉 1차 업로드 완료!"
echo "   - 서버 IP: $SERVER_IP"
echo "   - 대상 경로: ubuntu@$SERVER_IP:~/kids_library/backend"
echo "=================================================="
