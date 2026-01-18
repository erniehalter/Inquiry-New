# pingy_tunnel_monitor.py

import requests
import time
import logging
import sys

# --- Configuration ---
# URL for the *new* Healthchecks.io check dedicated to the tunnel
TUNNEL_HEALTHCHECK_URL = "https://hc-ping.com/f6640005-b9e8-48c9-8959-5e14695cc8a2"

# Local URL for Pinggy's Web Debugger API (ensure port matches -L flag in ssh command)
PINGGY_DEBUGGER_URL = "http://localhost:4300/urls"

# How often to check and ping (in seconds)
CHECK_INTERVAL_SECONDS = 60

# --- Logging Setup ---
# Log INFO level messages and above to standard output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - PINGGY_MONITOR - %(levelname)s - %(message)s', stream=sys.stdout)

def check_pinggy_tunnel_and_ping_hc():
    """
    Checks the local Pinggy debugger API for tunnel status and pings
    the dedicated Healthchecks.io URL accordingly.
    """
    tunnel_seems_up = False
    try:
        # Check if the Pinggy Web Debugger API is responsive
        response = requests.get(PINGGY_DEBUGGER_URL, timeout=5)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        if response.status_code == 200:
            logging.info(f"Successfully queried Pinggy debugger at {PINGGY_DEBUGGER_URL}. Tunnel client appears active.")
            tunnel_seems_up = True

    except requests.exceptions.ConnectionError:
        logging.error(f"Failed to connect to Pinggy debugger at {PINGGY_DEBUGGER_URL}. SSH tunnel process might be down.")
    except requests.exceptions.Timeout:
        logging.error(f"Timeout connecting to Pinggy debugger at {PINGGY_DEBUGGER_URL}.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error querying Pinggy debugger: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred while checking Pinggy debugger: {e}", exc_info=True)

    # --- Ping Healthchecks.io based on tunnel status ---
    if tunnel_seems_up:
        try:
            # Send success ping
            hc_response = requests.get(TUNNEL_HEALTHCHECK_URL, timeout=10)
            hc_response.raise_for_status()
            logging.info(f"Successfully pinged Healthchecks.io for tunnel status (UP) at {TUNNEL_HEALTHCHECK_URL}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to ping Healthchecks.io for tunnel status: {e}")
        except Exception as e:
             logging.error(f"An unexpected error occurred pinging Healthchecks.io: {e}", exc_info=True)
    else:
        logging.warning(f"Tunnel seems down or debugger unresponsive. Skipping Healthchecks.io success ping.")

# --- Main Loop ---
if __name__ == "__main__":
    logging.info(f"Starting Pinggy Tunnel Monitor.")
    logging.info(f"Checking local debugger at {PINGGY_DEBUGGER_URL}")
    logging.info(f"Pinging Healthchecks.io tunnel check at {TUNNEL_HEALTHCHECK_URL}")
    logging.info(f"Check interval: {CHECK_INTERVAL_SECONDS} seconds.")

    while True:
        check_pinggy_tunnel_and_ping_hc()
        logging.info(f"Sleeping for {CHECK_INTERVAL_SECONDS} seconds...")
        time.sleep(CHECK_INTERVAL_SECONDS)