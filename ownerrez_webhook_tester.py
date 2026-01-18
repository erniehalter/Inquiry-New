# ownerrez_webhook_tester.py

from flask import Flask, request, jsonify, Response
from functools import wraps
import json
import requests
import logging
import os
import subprocess
import threading
import sys
import time
import signal

# Import modules
import settings

# --- Configuration ---
WEBHOOK_USERNAME = "testuser"
WEBHOOK_PASSWORD = "testpass"
LISTEN_PORT = 5001
HEARTBEAT_INTERVAL_SECONDS = 60

# --- Flask App Setup ---
app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - WEBHOOK_TESTER - %(levelname)s - %(message)s')
log = logging.getLogger('werkzeug')
log.setLevel(logging.INFO)

# --- ANSI Color Codes ---
CYAN = '\033[96m'
BOLD = '\033[1m'
RESET = '\033[0m'

# --- Global variables for background threads ---
heartbeat_thread = None
stop_heartbeat = threading.Event()

# --- Basic Authentication ---
def check_auth(username, password):
    return username == WEBHOOK_USERNAME and password == WEBHOOK_PASSWORD

def authenticate():
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            logging.warning("!!! Authentication failed or not provided !!!")
            return authenticate()
        logging.info("--- Authentication Successful ---")
        return f(*args, **kwargs)
    return decorated

# --- Heartbeat Function ---
def send_heartbeat():
    logging.info("Heartbeat thread started.")
    while not stop_heartbeat.is_set():
        try:
            response = requests.get(settings.HEALTHCHECKS_PING_URL, timeout=15)
            response.raise_for_status() 
            logging.info("Heartbeat ping successful.")
        except Exception as e:
             logging.error(f"Heartbeat ping failed: {e}")

        if stop_heartbeat.wait(HEARTBEAT_INTERVAL_SECONDS):
             break

# --- Function to run main.py in background ---
def run_main_script_in_background():
    logging.info("Starting main.py execution in background...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_script_path = os.path.join(script_dir, 'main.py')

    if not os.path.exists(main_script_path):
        logging.error(f"main.py not found at: {main_script_path}")
        return

    process = None 
    try:
        python_executable = settings.PYTHON_EXECUTABLE
        process = subprocess.Popen(
            [python_executable, "-u", main_script_path], 
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, 
            text=True,           
            bufsize=1,           
            cwd=script_dir       
        )

        if process.stdout:
            for line in iter(process.stdout.readline, ''):
                print(line, end='')
                sys.stdout.flush() 
            process.stdout.close()

        process.wait()
    except Exception as e:
        logging.error(f"Error running main.py: {e}")

# --- Webhook Receiver Route ---
@app.route('/webhook/ownerrez', methods=['POST'])
@requires_auth
def ownerrez_webhook_listener():
    logging.info("\n--- Received OwnerRez Webhook ---")
    try:
        data = request.get_json()
        if data:
            logging.info(json.dumps(data, indent=2))
            entity_type = data.get('entity_type')
            action = data.get('action')

            is_inquiry = (entity_type == 'inquiry' and action == 'entity_create')
            is_test = (entity_type == 'api_application' and action == 'webhook_test')

            if is_inquiry or is_test:
                logging.info("Dispatching main.py execution.")
                threading.Thread(target=run_main_script_in_background, daemon=True).start()
            else:
                logging.info(f"Skipping trigger for {entity_type}/{action}")
    except Exception as e:
        logging.error(f"Error processing webhook: {e}")
        return jsonify({"status": "error"}), 500

    return jsonify({"status": "success"}), 200

# --- Shutdown Handler ---
def handle_shutdown_signal(signum, frame):
    stop_heartbeat.set()
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, handle_shutdown_signal)
    signal.signal(signal.SIGTERM, handle_shutdown_signal)

    heartbeat_thread = threading.Thread(target=send_heartbeat, daemon=True)
    heartbeat_thread.start()

    print(f"--- Starting OwnerRez Webhook Listener ---")
    print(f"Listening on http://0.0.0.0:{LISTEN_PORT}/webhook/ownerrez")
    app.run(host='0.0.0.0', port=LISTEN_PORT, debug=False, threaded=True)