# main.py

import logging
import settings
import gmail
import airbnb_automator

def main():
    settings.setup_logging()
    logging.info("--- Starting Airbnb Inquiry Automation (Webhook Triggered) ---")
    target_link = gmail.find_and_get_inquiry_thread_id(settings.EMAIL_SENDER_ADDRESS, settings.GMAIL_APP_PASSWORD)
    if not target_link:
        logging.info("No fresh inquiries found. Exiting.")
        return
    result = airbnb_automator.run_preapproval_flow(target_link)
    logging.info(f"Automation finished: {result}")

if __name__ == "__main__":
    main()