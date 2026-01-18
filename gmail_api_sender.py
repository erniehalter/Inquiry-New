# gmail_api_sender.py

import base64
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging
import asyncio
import settings 

async def send_email_with_screenshot_async(sender_email, recipient_email, subject, body_text, attachment_path):
    """Sends an email with a screenshot attachment using the Gmail API (async wrapper)."""
    await asyncio.to_thread(send_email_with_screenshot, sender_email, recipient_email, subject, body_text, attachment_path, settings.GMAIL_API_CREDENTIALS_FILE, settings.GMAIL_API_TOKEN_FILE, settings.SCOPES)

def send_email_with_screenshot(sender_email, recipient_email, subject, body_text, attachment_path, credentials_file, token_file, scopes):
    creds = None
    if os.path.exists(token_file):
        try:
            creds = Credentials.from_authorized_user_file(token_file, scopes)
        except Exception:
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_file):
                 raise FileNotFoundError(f"Missing {credentials_file}")
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, scopes)
            creds = flow.run_local_server(port=0)
        
        with open(token_file, 'w') as token:
            token.write(creds.to_json())

    try:
        service = build("gmail", "v1", credentials=creds)
        message = MIMEMultipart()
        message['To'] = recipient_email
        message['From'] = sender_email
        message['Subject'] = subject
        message.attach(MIMEText(body_text))

        if attachment_path and os.path.exists(attachment_path):
            part = MIMEBase('application', 'octet-stream')
            with open(attachment_path, 'rb') as file:
                part.set_payload(file.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(attachment_path)}"')
            message.attach(part)

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        service.users().messages().send(userId="me", body={'raw': raw}).execute()
        logging.info("Email report sent successfully.")
    except Exception as e:
        logging.error(f"Gmail API error: {e}")