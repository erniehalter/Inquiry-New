# gmail.py

import imaplib
import email
import re
import time
import datetime
import html 
import settings 

def get_email_parts(msg):
    text_parts, html_parts = [], []
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            if 'attachment' not in str(part.get('Content-Disposition')):
                try:
                    body = part.get_payload(decode=True)
                    if body:
                        charset = part.get_content_charset() or 'utf-8'
                        content = body.decode(charset, errors='replace')
                        if ctype == 'text/plain': text_parts.append(content)
                        elif ctype == 'text/html': html_parts.append(content)
                except Exception: pass
    else:
        try:
            body = msg.get_payload(decode=True)
            if body:
                content = body.decode(msg.get_content_charset() or 'utf-8', errors='replace')
                if msg.get_content_type() == 'text/plain': text_parts.append(content)
                else: html_parts.append(content)
        except Exception: pass
    return "".join(text_parts), "".join(html_parts)

def find_and_get_inquiry_thread_id(email_address, app_password):
    print("⏳ [GMAIL] Waiting 1s for email to send...")
    time.sleep(1)
    tiers = [(6, 5), (3, 10), (10, 30)]
    attempt = 0
    for count, delay in tiers:
        for _ in range(count):
            attempt += 1
            print(f"🔄 [LINK POLL] Attempt {attempt}...")
            try:
                mail = imaplib.IMAP4_SSL("imap.gmail.com")
                mail.login(email_address, app_password)
                mail.select("INBOX")
                query = f'(UNSEEN FROM "{settings.REQUIRED_SENDER}" SUBJECT "{settings.SUBJECT_STARTS_WITH}")'
                typ, data = mail.search("UTF-8", query)
                if typ == 'OK' and data[0]:
                    for mail_id in reversed(data[0].split()):
                        typ, msg_data = mail.fetch(mail_id, "(RFC822)")
                        msg = email.message_from_bytes(msg_data[0][1])
                        text, htm = get_email_parts(msg)
                        match = re.search(r'https://app\.ownerrez\.com/inquiries/\d+', text + htm)
                        if match:
                            url = html.unescape(match.group(0))
                            print(f"✅ [GMAIL] Link found: {url}")
                            mail.store(mail_id, '+FLAGS', '\\Seen')
                            mail.logout()
                            return url
                mail.logout()
            except Exception as e: print(f"⚠️ [GMAIL ERROR] {e}")
            time.sleep(delay)
    return None

def get_ownerrez_verification_code(email_address, app_password):
    print(f"\n📬 [GMAIL] Starting tiered code search...")
    for i in range(1, 25):
        wait_time = 5 if i <= 6 else 30
        print(f"🔄 [2FA POLL] Attempt {i}/24 | Check in {wait_time}s...")
        try:
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(email_address, app_password)
            mail.select("INBOX")
            query = f'(UNSEEN FROM "{settings.REQUIRED_SENDER}" SUBJECT "{settings.VERIFICATION_SUBJECT}")'
            typ, data = mail.search("UTF-8", query)
            if typ == 'OK' and data[0]:
                mail_id = data[0].split()[-1] 
                typ, msg_data = mail.fetch(mail_id, "(RFC822)")
                msg = email.message_from_bytes(msg_data[0][1])
                text, htm = get_email_parts(msg)
                code_match = re.search(r'\b(\d{6})\b', text + htm)
                if code_match:
                    code = code_match.group(1)
                    print(f"✅ [GMAIL] Found Code: {code}")
                    mail.store(mail_id, '+FLAGS', '\\Seen')
                    mail.logout()
                    return code
            if mail: mail.logout()
        except Exception as e: print(f"⚠️ [GMAIL ERROR] {e}")
        time.sleep(wait_time)
    return None