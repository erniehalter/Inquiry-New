import os
import time
import re
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

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
    match = re.search(r'\b\d{6}\b', msg.get('snippet', ''))
    return match.group(0) if match else None

def run_automation(target_inquiry_url=None):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # 1. Open main site and wait
        page.goto("https://app.ownerrez.com")
        time.sleep(5)
        
        # 2. Type credentials
        print("⌨️ Entering credentials...")
        page.keyboard.type(OWNERREZ_EMAIL)
        page.keyboard.press("Tab")
        page.keyboard.type(OWNERREZ_PASSWORD)
        page.keyboard.press("Enter")
        
        # 3. Wait for 2FA page
        time.sleep(5)
        
        # 4. Poll Gmail for code
        print("🔄 Polling Gmail for 2FA...")
        service = get_gmail_service()
        code = None
        for _ in range(24):
            code = get_ownerrez_2fa_code(service)
            if code: break
            time.sleep(5)
            
        if code:
            print(f"✅ Found code: {code}. Injecting...")
            page.keyboard.type(code)
            page.keyboard.press("Enter")
        
        # 5. Final wait and redirect to Inbox
        time.sleep(5)
        page.goto("https://app.ownerrez.com/inbox")
        print("🏁 Arrived at Inbox.")
        time.sleep(10)
        browser.close()

if __name__ == "__main__":
    run_automation()