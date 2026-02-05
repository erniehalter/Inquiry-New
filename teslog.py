import os
import time
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()
EMAIL = os.getenv("OWNERREZ_EMAIL")
PASS = os.getenv("OWNERREZ_PASSWORD")

def test_login():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        print("📡 Loading Login Page...")
        page.goto("https://app.ownerrez.com/accounts/login")
        
        page.fill("input[name='Email']", EMAIL)
        page.fill("input[name='Password']", PASS)
        page.click("button[type='submit']")
        
        print("🔑 Credentials submitted. Check for 2FA or Dashboard.")
        time.sleep(10) # Pause to observe result
        
        if "Dashboard" in page.title():
            print("✅ Login Successful.")
        else:
            print(f"❌ Current Page: {page.title()}")
            
        browser.close()

if __name__ == "__main__":
    test_login()