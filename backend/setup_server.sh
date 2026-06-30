#!/bin/bash
# AWS Lightsail (Ubuntu 22.04) 서버 환경 자동 구성 스크립트
# 실행 방법: bash ~/kids_library/backend/setup_server.sh

echo "=================================================="
echo "⚙️ AWS Lightsail 서버 구성 시작 (Nginx + Python venv + Systemd)"
echo "=================================================="

# 1. 패키지 업데이트 및 시스템 기본 도구 설치
echo "🔄 시스템 패키지 업데이트 및 필수 패키지 설치 중..."
sudo apt-get update -y
sudo apt-get install -y python3-pip python3-venv nginx git curl

# 2. 파이썬 가상환경 구성
echo "🐍 파이썬 가상환경 생성 및 라이브러리 설치 중..."
python3 -m venv ~/venv
~/venv/bin/pip install --upgrade pip
~/venv/bin/pip install -r ~/kids_library/backend/requirements.txt
# Gunicorn 추가 설치 (상용 웹 서버 안정성용)
~/venv/bin/pip install gunicorn

# 3. Systemd 서비스 파일 등록 (FastAPI 자동 실행 및 무중단 가동)
echo "⚙️ FastAPI systemd 서비스 등록 중..."
sudo bash -c 'cat > /etc/systemd/system/fastapi.service <<EOF
[Unit]
Description=Kids Library FastAPI Backend Application
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/kids_library/backend
ExecStart=/home/ubuntu/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --workers 2
Restart=always
EnvironmentFile=/home/ubuntu/kids_library/backend/.env

[Install]
WantedBy=multi-user.target
EOF'

# FastAPI 서비스 활성화 및 시작
sudo systemctl daemon-reload
sudo systemctl enable fastapi
sudo systemctl restart fastapi

# 4. Nginx 역방향 프록시 설정 (80포트 요청을 8000 uvicorn 포트로 포워딩)
echo "🌐 Nginx 웹 서버 설정 구성 중..."
sudo bash -c 'cat > /etc/nginx/sites-available/fastapi <<EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF'

# Nginx 활성화
sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -sf /etc/nginx/sites-available/fastapi /etc/nginx/sites-enabled/
sudo systemctl restart nginx

echo "=================================================="
echo "🎉 AWS Lightsail 백엔드 인프라 기본 셋업이 완료되었습니다!"
echo "   - FastAPI 상태: \$(systemctl is-active fastapi)"
echo "   - Nginx 상태: \$(systemctl is-active nginx)"
echo "=================================================="
