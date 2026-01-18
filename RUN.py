import subprocess
import time
import os

def run_tabs():
    # The path to your project
    project_path = "/Users/erniehalter/Desktop/PythonApps/WORKING/Inquiry-New"
    
    # FIX: Changed to use 'ServerAliveInterval=60' (no quotes needed) to fix AppleScript error
    pinggy_cmd = f"cd {project_path} && autossh -M 0 -t -p 443 -o ServerAliveInterval=60 -o ServerAliveCountMax=3 -R 80:localhost:5001 -L 4300:localhost:4300 Sdxfy5hKNil+force+http@a.pinggy.io"
    
    # Command for the Webhook Tester
    tester_cmd = f"cd {project_path} && source venv/bin/activate && python3 ownerrez_webhook_tester.py"
    
    # Command for the Monitor
    monitor_cmd = f"cd {project_path} && source venv/bin/activate && python3 pingy_tunnel_monitor.py"

    commands = [pinggy_cmd, tester_cmd, monitor_cmd]

    for cmd in commands:
        # This AppleScript opens a new terminal tab and runs the command
        # We replace any remaining double quotes with escaped quotes just in case
        safe_cmd = cmd.replace('"', '\\"')
        applescript = f'tell application "Terminal" to do script "{safe_cmd}"'
        subprocess.run(["osascript", "-e", applescript])
        time.sleep(1)

    print("✅ All tabs opened with corrected tunnel settings.")

if __name__ == "__main__":
    # Optional: Kill any existing autossh processes to start fresh
    subprocess.run(["pkill", "-f", "autossh"])
    run_tabs()