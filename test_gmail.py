# test_gmail.py

import settings
import gmail
import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

print("--- Starting 24h Inbox Search Test ---")

try:
    # This will now look for READ or UNREAD emails from the last 24 hours
    extracted_link = gmail.find_and_get_inquiry_thread_id(
        settings.EMAIL_SENDER_ADDRESS, 
        settings.GMAIL_APP_PASSWORD
    )

    if extracted_link:
        print("\n✅ SUCCESS!")
        print(f"   Extracted OwnerRez Link: {extracted_link}")
    else:
        print("\n❌ Failed to find a matching inquiry within the last 24 hours.")

except Exception as e:
    print(f"\n💥 An error occurred: {e}")

print("\n--- Test Complete ---")