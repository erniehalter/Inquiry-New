import os
import time
import re
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# --- Configuration (Matches airbnb_automator.py) ---
load_dotenv()
OWNERREZ_EMAIL = os.getenv("OWNERREZ_EMAIL")
OWNERREZ_PASSWORD = os.getenv("OWNERREZ_PASSWORD")
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

def get_ownerrez_2fa_code(service):
    query = "from:no-reply@ownerrez.com \"Your OwnerRez verification code is\""
    results = service.users().messages().list(userId='me', q=query, maxResults=1).execute()
    messages = results.get('messages', [])
    if not messages: return None
    msg = service.users().messages().get(userId='me', id=messages[0]['id']).execute()
    snippet = msg.get('snippet', '')
    match = re.search(r'\b\d{6}\b', snippet)
    return match.group(0) if match else None

def test_login_logic():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        try:
            # Navigating to a deep link to trigger login, exactly like the automator
            print("📡 Loading OwnerRez Inquiry Page...")
            page.goto("https://app.ownerrez.com/inquiries/807247433")

            # Identical Login/2FA block from airbnb_automator.py
            if "Log In" in page.title() or page.query_selector("input[name='Email']"):
                print(f"🔑 Login required. Injecting {OWNERREZ_EMAIL}...")
                page.fill("input[name='Email']", OWNERREZ_EMAIL)
                page.fill("input[name='Password']", OWNERREZ_PASSWORD)
                page.click("button[type='submit']")
                
                if page.query_selector("input[name='Code']"):
                    print("⚡ 2FA detected. Polling Gmail...")
                    service = get_gmail_service()
                    code = None
                    for i in range(24):
                        print(f"🔄 [2FA POLL] Attempt {i+1}/24...")
                        time.sleep(5)
                        code = get_ownerrez_2fa_code(service)
                        if code:
                            print(f"✅ Found Code: {code}")
                            break
                    
                    if code:
                        page.fill("input[name='Code']", code)
                        page.click("button[type='submit']")
                        page.wait_for_load_state("networkidle")

            print(f"🏁 Success. Final Page Title: {page.title()}")
            time.sleep(5)

        finally:
            browser.close()

if __name__ == "__main__":
    test_login_logic()