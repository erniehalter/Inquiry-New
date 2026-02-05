import os
import io
import time
import re
from datetime import datetime
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import google.generativeai as genai
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64

# --- Configuration (Loaded from .env) ---
load_dotenv()
EMAIL_SENDER_ADDRESS = os.getenv("EMAIL_SENDER_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

# OwnerRez Login Credentials
OWNERREZ_EMAIL = os.getenv("OWNERREZ_EMAIL")
OWNERREZ_PASSWORD = os.getenv("OWNERREZ_PASSWORD")

# Email search criteria
SUBJECT_STARTS_WITH = "Inquiry from"

# Gemini API Key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Gmail API Scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def get_latest_inquiry_link(service, target_inquiry_id=None):
    query = f"from:{EMAIL_SENDER_ADDRESS} subject:\"{SUBJECT_STARTS_WITH}\""
    results = service.users().messages().list(userId='me', q=query, maxResults=10).execute()
    messages = results.get('messages', [])

    if not messages:
        return None

    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
        payload = msg_data.get('payload', {})
        parts = payload.get('parts', [])
        body = ""

        if not parts:
            body = base64.urlsafe_b64decode(payload.get('body', {}).get('data', '')).decode('utf-8')
        else:
            for part in parts:
                if part.get('mimeType') == 'text/plain':
                    body = base64.urlsafe_b64decode(part.get('body', {}).get('data', '')).decode('utf-8')
                    break
        
        links = re.findall(r'https://app\.ownerrez\.com/inquiries/\d+', body)
        if links:
            found_link = links[0]
            if target_inquiry_id:
                if str(target_inquiry_id) in found_link:
                    return found_link
            else:
                return found_link
    return None

def get_ownerrez_2fa_code(service):
    query = "from:no-reply@ownerrez.com \"Your OwnerRez verification code is\""
    results = service.users().messages().list(userId='me', q=query, maxResults=1).execute()
    messages = results.get('messages', [])

    if not messages:
        return None

    msg = service.users().messages().get(userId='me', id=messages[0]['id']).execute()
    snippet = msg.get('snippet', '')
    match = re.search(r'\b\d{6}\b', snippet)
    return match.group(0) if match else None

def run_automation(target_inquiry_url=None, target_inquiry_id=None):
    print(f"\n🚀 [START] Target Inquiry: {target_inquiry_url if target_inquiry_url else 'Latest'} (Attempt 1/3)")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        try:
            # 1. Load Page
            print("📡 [1/4] Loading page...")
            page.goto(target_inquiry_url)

            # 2. Handle Login/2FA
            if "Log In" in page.title() or page.query_selector("input[name='Email']"):
                print("🔑 [2/4] Login required. Injecting credentials instantly...")
                page.fill("input[name='Email']", OWNERREZ_EMAIL)
                page.fill("input[name='Password']", OWNERREZ_PASSWORD)
                page.click("button[type='submit']")
                
                if page.query_selector("input[name='Code']"):
                    print("⚡ [ACTION] Login sent. Polling Gmail for 2FA...")
                    service = get_gmail_service()
                    code = None
                    for i in range(24):
                        print(f"🔄 [2FA POLL] Attempt {i+1}/24 | Check in 5s...")
                        time.sleep(5)
                        code = get_ownerrez_2fa_code(service)
                        if code:
                            print(f"✅ [GMAIL] Found Code: {code}")
                            break
                    
                    if code:
                        print(f"🔢 [ACTION] Injecting code: {code}")
                        page.fill("input[name='Code']", code)
                        page.click("button[type='submit']")
                        print("⏳ [WAIT] Waiting for dashboard to load after 2FA...")
                        page.wait_for_load_state("networkidle")
                    else:
                        print("❌ [ERROR] 2FA timeout.")
                        return

            # 3. Handle Conflicts (NEW FIX)
            if "Row Version Conflict" in page.content() or "Database Concurrency Error" in page.content():
                print("💥 [CONFLICT] Stale data detected. Refreshing...")
                page.reload()
                page.wait_for_load_state("networkidle")

            # 4. Pre-Approve Logic
            print("🖱️ [3/4] Searching for Pre-Approve button...")
            pre_approve_button = page.query_selector("a:has-text('Pre-Approve')")
            
            if pre_approve_button:
                print("✅ [FOUND] Clicking Pre-Approve...")
                pre_approve_button.click()
                page.wait_for_load_state("networkidle")
                
                # Double-check for conflict after click
                if "Row Version Conflict" in page.content():
                    print("💥 [CONFLICT] Database locked after click. Final Refresh...")
                    page.reload()
                    page.wait_for_load_state("networkidle")
                    # Re-find button if necessary
                    pre_approve_button = page.query_selector("a:has-text('Pre-Approve')")
                    if pre_approve_button: pre_approve_button.click()

                print("🔘 [ACTION] Confirming Pre-Approval...")
                confirm_button = page.query_selector("button:has-text('Pre-Approve')")
                if confirm_button:
                    confirm_button.click()
                    print("🎉 [SUCCESS] Inquiry Pre-Approved.")
                else:
                    print("⚠️ [WARN] Final confirmation button not found.")
            else:
                print("ℹ️ [SKIP] Pre-Approve button not available (already approved or expired).")

        except Exception as e:
            print(f"💥 [ATTEMPT FAILED] Error: {str(e)}")
        finally:
            print("🏁 Closing browser session.")
            browser.close()

if __name__ == "__main__":
    import sys
    # If triggered by webhook/main.py, an inquiry ID might be passed
    inquiry_id = sys.argv[1] if len(sys.argv) > 1 else None
    
    gmail_service = get_gmail_service()
    
    # Poll for the email/link
    inquiry_url = None
    for i in range(10):
        print(f"🔄 [LINK POLL] Attempt {i+1}...")
        inquiry_url = get_latest_inquiry_link(gmail_service, inquiry_id)
        if inquiry_url:
            print(f"✅ [GMAIL] Link found: {inquiry_url}")
            break
        time.sleep(10)
    
    if inquiry_url:
        run_automation(target_inquiry_url=inquiry_url, target_inquiry_id=inquiry_id)
    else:
        print("❌ [ERROR] Could not find inquiry link in Gmail.")