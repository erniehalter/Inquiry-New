import os
import time
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()
# Match variables in your settings.py and .env
EMAIL = os.getenv("OWNERREZ_EMAIL")
PASS = os.getenv("OWNERREZ_PASSWORD")

def test_login():
    if not EMAIL or not PASS:
        print("❌ ERROR: Credentials missing from .env (Check OWNERREZ_EMAIL and OWNERREZ_PASSWORD)")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        print(f"📡 Loading Login Page for {EMAIL}...")
        page.goto("https://app.ownerrez.com")
        
        page.fill("input[name='Email']", EMAIL)
        page.fill("input[name='Password']", PASS)
        page.click("button[type='submit']")
        
        print("🔑 Credentials submitted. Check for 2FA or Dashboard.")
        time.sleep(10) 
        
        if "Dashboard" in page.title():
            print("✅ Login Successful.")
        else:
            print(f"❌ Current Page Title: {page.title()}")
            
        browser.close()

if __name__ == "__main__":
    test_login()