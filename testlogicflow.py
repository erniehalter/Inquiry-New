# test_login_flow.py

import airbnb_automator
import logging

# Basic logging for clean output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_test():
    print("\n--- 🧪 STARTING SIMPLIFIED LOGIN TEST ---")
    print("Sequence: Open -> Wait 5s -> Type -> Wait 5s -> 2FA Poll -> Inbox\n")
    
    try:
        # Executes the simplified sequence in airbnb_automator.py
        airbnb_automator.run_automation()
    except Exception as e:
        print(f"\n💥 TEST CRASHED: {e}")

if __name__ == "__main__":
    run_test()