# RUN.py

import os
import subprocess
import time
import sys

# --- Configuration ---
PROJECT_DIR = "/Users/erniehalter/Desktop/PythonApps/WORKING/Inquiry-New"
SSH_CMD = "autossh -M 0 -N -p 443 -o ServerAliveInterval=60 -o ServerAliveCountMax=3 -R0:localhost:5001 -L4300:localhost:4300 Sdxfy5hKNil@a.pinggy.io"

def cleanup_ports():
    """Kills processes on 5001 and 4300 to prevent 'Address already in use'."""
    for port in [5001, 4300]:
        try:
            pid = subprocess.check_output(["lsof", "-t", f"-i:{port}"]).decode().strip()
            if pid:
                os.system(f"kill -9 {pid}")
        except: pass
    os.system("pkill -f autossh > /dev/null 2>&1")

def run_applescript(script):
    subprocess.run(["osascript", "-e", script])

def main():
    cleanup_ports()
    print("🧹 Ports cleaned. Launching Inquiry-New tabs...")

    # Define the commands for each tab
    cmd_listener = f"cd {PROJECT_DIR} && source venv/bin/activate && python3 ownerrez_webhook_tester.py"
    cmd_tunnel = f"cd {PROJECT_DIR} && {SSH_CMD}"
    cmd_monitor = f"cd {PROJECT_DIR} && source venv/bin/activate && python3 pingy_tunnel_monitor.py"

    # Tab 1: Webhook Listener
    run_applescript(f'tell application "Terminal" to do script "{cmd_listener}" in front window')
    
    # Tab 2: SSH Tunnel
    run_applescript('tell application "System Events" to tell process "Terminal" to keystroke "t" using command down')
    time.sleep(1)
    run_applescript(f'tell application "Terminal" to do script "{cmd_tunnel}" in front window')
    
    # Tab 3: Tunnel Monitor
    run_applescript('tell application "System Events" to tell process "Terminal" to keystroke "t" using command down')
    time.sleep(1)
    run_applescript(f'tell application "Terminal" to do script "{cmd_monitor}" in front window')

    print("✅ All tabs opened successfully.")

if __name__ == "__main__":
    main()