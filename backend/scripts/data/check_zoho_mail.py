import os
import sys
import imaplib
import email
from email.header import decode_header
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

ZOHO_EMAIL = os.getenv("ZOHO_EMAIL")
ZOHO_PASSWORD = os.getenv("ZOHO_PASSWORD")  # Zoho 계정에 2단계 인증이 설정되어 있다면 '앱 비밀번호(App Password)'를 사용해야 합니다.
IMAP_SERVER = os.getenv("ZOHO_IMAP_SERVER", "imap.zoho.com")

def check_zoho_mail():
    if not ZOHO_EMAIL or not ZOHO_PASSWORD:
        print("❌ 오류: .env 파일에 ZOHO_EMAIL, ZOHO_PASSWORD를 설정해주세요.")
        sys.exit(1)

    try:
        print(f"🔄 '{ZOHO_EMAIL}' 계정의 안 읽은 메일을 확인하는 중... (IMAP: {IMAP_SERVER})")
        # IMAP 서버 접속
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, 993)
        mail.login(ZOHO_EMAIL, ZOHO_PASSWORD)
        
        # 받은 편지함 선택
        mail.select("inbox")
        
        # '안 읽은 메일(UNSEEN)' 검색
        status, messages = mail.search(None, "UNSEEN")
        
        if status != "OK":
            print("메일을 가져오는 데 실패했습니다.")
            return

        email_ids = messages[0].split()
        
        if not email_ids:
            print("✅ 현재 새로 도착한 메일(안 읽은 메일)이 없습니다.")
            return
            
        print(f"\n📬 총 {len(email_ids)}개의 안 읽은 메일이 있습니다.\n")
        print("=" * 60)
        
        # 최근 5개의 메일만 출력 (너무 많은 출력을 방지)
        for e_id in email_ids[-5:]:
            res, msg_data = mail.fetch(e_id, "(RFC822)")
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    # 제목 디코딩
                    subject_data = decode_header(msg["Subject"])[0]
                    subject = subject_data[0]
                    encoding = subject_data[1]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                        
                    # 보낸 사람 디코딩
                    from_data = decode_header(msg.get("From"))[0]
                    from_ = from_data[0]
                    from_encoding = from_data[1]
                    if isinstance(from_, bytes):
                        from_ = from_.decode(from_encoding if from_encoding else "utf-8")
                    
                    print(f"보낸 사람 : {from_}")
                    print(f"제    목 : {subject}")
                    
                    # (선택) 메일 본문 내용의 앞부분 요약이 필요하다면 아래 로직 확장 가능
                    # if msg.is_multipart(): ...
                    
                    print("-" * 60)
                    
        # 접속 종료
        mail.close()
        mail.logout()
        print("\n✅ 메일 확인 완료.")
        
    except imaplib.IMAP4.error as e:
        print(f"❌ IMAP 연결 오류 (아이디/비밀번호나 IMAP 활성화 여부를 확인해주세요): {e}")
    except Exception as e:
        print(f"❌ 알 수 없는 오류 발생: {e}")

if __name__ == "__main__":
    check_zoho_mail()
