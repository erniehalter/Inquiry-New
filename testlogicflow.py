# test_login_flow.py

import airbnb_automator
import settings
import logging

# Set up logging to see the console output clearly
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Target the Inbox to test general login persistence
TEST_INQUIRY_URL = "https://app.ownerrez.com/inbox"

def run_test():
    print("\n--- 🧪 STARTING OWNERREZ LOGIN TEST ---")
    print(f"Targeting: {TEST_INQUIRY_URL}")
    print("Watching for: Credentials -> 2FA Poll -> Inbox Load\n")
    
    try:
        # Calls the existing automation logic in airbnb_automator.py
        airbnb_automator.run_automation(target_inquiry_url=TEST_INQUIRY_URL)
    except Exception as e:
        print(f"\n💥 TEST CRASHED: {e}")

if __name__ == "__main__":
    run_test()