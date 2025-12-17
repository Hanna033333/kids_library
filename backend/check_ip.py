#!/usr/bin/env python
"""
현재 서버의 공인 IP 주소 확인
"""

import requests

def get_public_ip():
    """공인 IP 주소 조회"""
    
    services = [
        "https://api.ipify.org",
        "https://ifconfig.me/ip",
        "https://icanhazip.com",
        "https://ident.me"
    ]
    
    for service in services:
        try:
            print(f"Checking {service}...")
            response = requests.get(service, timeout=5)
            if response.status_code == 200:
                ip = response.text.strip()
                print(f"✅ Your public IP: {ip}")
                return ip
        except Exception as e:
            print(f"  Failed: {e}")
            continue
    
    print("❌ Could not determine public IP")
    return None

if __name__ == "__main__":
    print("="*60)
    print("🌐 공인 IP 주소 확인")
    print("="*60)
    print()
    
    ip = get_public_ip()
    
    if ip:
        print()
        print("="*60)
        print(f"📍 Data Library API에 등록할 IP: {ip}")
        print("="*60)
        print()
        print("다음 사이트에서 IP를 등록하세요:")
        print("https://www.data4library.kr/")
