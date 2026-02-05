# airbnb_automator.py

import os
import time
import re
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64

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
        try:
            page.goto(target_inquiry_url)
            if "Log In" in page.title() or page.query_selector("input[name='Email']"):
                page.fill("input[name='Email']", OWNERREZ_EMAIL)
                page.fill("input[name='Password']", OWNERREZ_PASSWORD)
                page.click("button[type='submit']")
                
                if page.query_selector("input[name='Code']"):
                    service = get_gmail_service()
                    code = None
                    for i in range(24):
                        time.sleep(5)
                        code = get_ownerrez_2fa_code(service)
                        if code: break
                    
                    if code:
                        page.fill("input[name='Code']", code)
                        page.click("button[type='submit']")
                        page.wait_for_load_state("networkidle")

            # Final check for login success
            time.sleep(5) 
        finally:
            browser.close()