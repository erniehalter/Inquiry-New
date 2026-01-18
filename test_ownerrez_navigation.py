# test_ownerrez_navigation.py

import os
import time
from playwright.sync_api import sync_playwright
import settings

# --- Configuration ---
# Update this to your actual macOS user folder name
USER_PATH = "/Users/erniehalter/Library/Application Support/Google/Chrome"
PROFILE_NAME = "Default" # Or "Profile 1", "Profile 2", etc.
TARGET_URL = "https://app.ownerrez.com/inquiries/807247433"

def test_navigation():
    print(f"--- Testing OwnerRez Session Persistence ---")
    print(f"Target: {TARGET_URL}")

    with sync_playwright() as p:
        # We use launch_persistent_context to 'inherit' your Chrome session
        context = p.chromium.launch_persistent_context(
            user_data_dir=os.path.join(USER_PATH, PROFILE_NAME),
            headless=False, # We want to see it happen
            args=["--no-sandbox"]
        )

        page = context.new_page()

        try:
            print("Navigating...")
            page.goto(TARGET_URL, wait_until="networkidle")
            
            # Wait to see if we land on the dashboard or a login page
            time.sleep(5) 
            
            current_url = page.url
            if "login" in current_url.lower():
                print("❌ Result: Redirected to LOGIN. Session not found.")
            else:
                print(f"✅ Result: Successfully loaded page: {current_url}")
                
                # Check for any button that looks like 'Pre-approve'
                # Adjusting selector based on standard OwnerRez UI patterns
                preapprove_btn = page.query_selector("text='Pre-approve'")
                if preapprove_btn:
                    print("🎯 Found 'Pre-approve' button on the page!")
                else:
                    print("ℹ️ Page loaded, but 'Pre-approve' button not found (it might already be handled).")

        except Exception as e:
            print(f"💥 Error: {e}")
        finally:
            print("Closing in 10 seconds...")
            time.sleep(10)
            context.close()

if __name__ == "__main__":
    test_navigation()