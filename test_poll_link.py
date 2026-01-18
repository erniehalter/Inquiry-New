# test_poll_link.py

import imaplib
import email
import datetime
import html
import re
import settings
import gmail 

def test_gmail_link_polling():
    print("🧪 [VERBOSE TEST] Starting Gmail Inquiry Link Polling Test...")
    print(f"📧 Targeting Sender: '{settings.REQUIRED_SENDER}'")
    print(f"📋 Subject Starts With: '{settings.SUBJECT_STARTS_WITH}'")
    
    try:
        # 1. Connect and Login
        print("\n📡 [1/3] Connecting to IMAP...")
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(settings.EMAIL_SENDER_ADDRESS, settings.GMAIL_APP_PASSWORD)
        print("✅ Login successful.")

        # 2. Search Strategy
        mail.select("INBOX")
        # We use today's date to filter out old test inquiries
        since_date = (datetime.date.today()).strftime("%d-%b-%Y")
        
        # We search for UNREAD (UNSEEN) emails matching your criteria
        query = f'(UNSEEN FROM "{settings.REQUIRED_SENDER}" SUBJECT "{settings.SUBJECT_STARTS_WITH}" SINCE {since_date})'
        print(f"🔍 [2/3] Sending Query: {query}")
        
        typ, data = mail.search("UTF-8", query)
        
        if typ != 'OK':
            print(f"❌ Search failed with status: {typ}")
            return

        email_ids = data[0].split()
        print(f"📊 Found {len(email_ids)} matching unread emails.")

        # 3. Content Inspection
        print("\n📖 [3/3] Inspecting email contents...")
        if not email_ids:
            print("🛑 NO EMAILS FOUND. Ensure the email is marked as UNREAD in your inbox.")
            print("   Check if the 'From' address or 'Subject' in settings.py is slightly different.")

        for mail_id in reversed(email_ids):
            print(f"\n--- Checking Email ID: {mail_id.decode()} ---")
            typ, msg_data = mail.fetch(mail_id, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])
            
            subject = msg.get("Subject")
            date = msg.get("Date")
            print(f"🔹 Subject: {subject}")
            print(f"🔹 Date: {date}")

            # Using our helper to strip text and html
            text, htm = gmail.get_email_parts(msg) 
            
            # Look for the specific OwnerRez Inquiry Link
            ownerrez_url_pattern = r'https://app\.ownerrez\.com/inquiries/\d+'
            match = re.search(ownerrez_url_pattern, text + htm)
            
            if match:
                url = html.unescape(match.group(0))
                print(f"🎯 MATCH FOUND: {url}")
            else:
                print("⚠️ NO LINK FOUND in this email.")
                print(f"📝 TEXT PREVIEW: {text[:300]}...")

        mail.logout()
        print("\n🏁 Test complete.")

    except Exception as e:
        print(f"💥 TEST CRASHED: {e}")

if __name__ == "__main__":
    # Corrected function call
    test_gmail_link_polling()