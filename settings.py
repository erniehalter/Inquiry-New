# settings.py

import logging
import os
import io
from datetime import datetime

# --- Configuration ---
EMAIL_SENDER_ADDRESS = "erniehalter@gmail.com"
GMAIL_APP_PASSWORD = "pskhfsgvokmhdprx" 

# OwnerRez Login Credentials
OWNERREZ_EMAIL = "erniehalter+ownerrez@gmail.com"
OWNERREZ_PASSWORD = "Frofro42!"

# Email search criteria
SUBJECT_STARTS_WITH = "Inquiry from" 
REQUIRED_SENDER = "alerts@ownerrez.com" 
VERIFICATION_SUBJECT = "account verification code"

# Playwright Configuration
HEADLESS = False
PLAYWRIGHT_TIMEOUT = 60000 
INITIAL_BUTTON_TIMEOUT = 10000 
ALREADY_ANSWERED_CHECK_TIMEOUT = 10000 

# Screenshot Configuration
SCREENSHOT_DIR = "screenshots"

# Gmail API Configuration
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
GMAIL_API_TOKEN_FILE = "token.json"
GMAIL_API_CREDENTIALS_FILE = "credentials.json" 

# Email recipient for screenshots
EMAIL_RECIPIENT_ADDRESS = "erniehalter@gmail.com"

# --- Path to Virtual Environment Python ---
PYTHON_EXECUTABLE = "/Users/erniehalter/Desktop/PythonApps/WORKING/Inquiry-New/venv/bin/python3"

# Healthchecks.io URLs
HEALTHCHECKS_PING_URL = "https://hc-ping.com/7885bcf9-d738-4949-8262-3dfd3069569d"
TUNNEL_HEALTHCHECK_URL = "https://hc-ping.com/f6640005-b9e8-48c9-8959-5e14695cc8a2"

# --- Utility Functions ---

def setup_logging(level=logging.INFO):
    """Sets up basic logging."""
    logger = logging.getLogger()
    if not logger.hasHandlers():
        logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s')
        logger.setLevel(level)

def ensure_dir_exists(directory):
    """Ensures a directory exists."""
    os.makedirs(directory, exist_ok=True)

def capture_logs():
    """Starts capturing log output to a string."""
    log_stream = io.StringIO()
    stream_handler = logging.StreamHandler(log_stream)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    stream_handler.setFormatter(formatter)
    logging.root.addHandler(stream_handler)
    stream_handler.setLevel(logging.root.level)
    return log_stream, stream_handler

def stop_capturing_logs(stream_handler):
    """Stops capturing log output and returns the captured string."""
    if stream_handler in logging.root.handlers:
        logging.root.removeHandler(stream_handler)
    captured_logs = stream_handler.stream.getvalue()
    stream_handler.close()
    return captured_logs

def generate_screenshot_path(status):
    """Generates a screenshot filename with timestamp based on status."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{status}_preapprove_attempt_{timestamp}.png"
    ensure_dir_exists(SCREENSHOT_DIR)
    return os.path.join(SCREENSHOT_DIR, filename)