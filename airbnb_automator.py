import time
import logging
from playwright.sync_api import sync_playwright
import settings
import gmail

def run_preapproval_flow(target_url):
    settings.setup_logging()
    print(f"\n🚀 [START] Target Inquiry: {target_url}")
    INSTANT_DELAY = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=settings.HEADLESS)
        context = browser.new_context()
        page = context.new_page()

        try:
            print("📡 [1/4] Loading page...")
            page.goto(target_url, wait_until="networkidle")
            
            # --- AUTHENTICATION ---
            if "login" in page.url.lower():
                print("🔑 [2/4] Login required. Injecting credentials instantly...")
                time.sleep(1)
                page.keyboard.type(settings.OWNERREZ_EMAIL, delay=INSTANT_DELAY)
                page.keyboard.press("Tab")
                page.keyboard.type(settings.OWNERREZ_PASSWORD, delay=INSTANT_DELAY)
                page.keyboard.press("Enter")
                
                print("⚡ [ACTION] Login sent. Polling Gmail for 2FA...")
                code = gmail.get_ownerrez_verification_code(
                    settings.EMAIL_SENDER_ADDRESS, 
                    settings.GMAIL_APP_PASSWORD
                )
                
                if code:
                    print(f"🔢 [ACTION] Injecting code: {code}")
                    time.sleep(2) 
                    page.keyboard.type(code, delay=INSTANT_DELAY)
                    page.keyboard.press("Enter")
                    page.wait_for_load_state("networkidle")
                else:
                    return "FAIL: No 2FA code found"

            # --- PRE-APPROVAL ACTION ---
            print("🔍 [3/4] Locating 'Pre-Approve' button...")
            btn_selector = "text='Pre-Approve'"
            
            try:
                # We try to find the button for 10 seconds
                page.wait_for_selector(btn_selector, state="visible", timeout=10000)
                print("🎯 [MATCH] Clicking Pre-Approve...")
                page.click(btn_selector)
                
                # --- NEW HAMMER LOGIC ---
                # We blindly press Enter 4 times, 2 seconds apart, to catch the popup whenever it arrives.
                print("🔨 [ACTION] Brute-force confirming (Pressing Enter 4x over 8s)...")
                for i in range(4):
                    print(f"   👉 Pressing Enter ({i+1}/4)...")
                    page.keyboard.press("Enter")
                    time.sleep(2)
                
                # Buffer for server processing after the final press
                time.sleep(2)
            except Exception as e:
                # If button is missing, it might already be done. Move to check.
                print(f"ℹ️ Error during interaction: {e}. Moving to final verification...")

            # --- VERIFICATION PHASE ---
            print("🧐 [4/4] Verifying final status...")
            # We try to reload to see the updated status badge
            try:
                page.reload(wait_until="networkidle", timeout=15000)
            except Exception:
                print("⚠️ Reload timed out, checking content anyway...")
            
            content = page.content()
            
            # Check success indicators from screenshots
            if "Pre-Approved" in content:
                print("✅ [VERIFIED] Status: Pre-Approved badge found.")
                return "SUCCESS: PRE-APPROVED"
            elif "Quoted" in content:
                print("✅ [VERIFIED] Status: Quoted badge found.")
                return "SUCCESS: QUOTED"
            else:
                print("⚠️ [WARNING] No success badge found on page.")
                screenshot_path = settings.generate_screenshot_path("verification_failed")
                page.screenshot(path=screenshot_path)
                return "FAIL: Verification Failed"

        except Exception as e:
            print(f"💥 [CRASH] Fatal Error: {e}")
            return f"FAIL: {e}"
        finally:
            print("🏁 Closing browser session.")
            browser.close()

if __name__ == "__main__":
    # Test link
    run_preapproval_flow("https://app.ownerrez.com/inquiries/807248133")