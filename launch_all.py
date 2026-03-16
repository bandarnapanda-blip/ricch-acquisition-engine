import subprocess
import time
import os
import sys
import logging

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RI2CH_Launcher")

def start_process(name, script):
    """Start a subprocess using the local venv python."""
    logger.info(f"Starting {name}...")
    python_path = os.path.join("venv", "Scripts", "python.exe")
    if not os.path.exists(python_path):
        python_path = sys.executable
        
    cmd = f'"{python_path}" {script}'
    try:
        # Pumping stdout/stderr to main console for debugging
        process = subprocess.Popen(
            cmd,
            shell=True,
            # Removed pipe to allow logs to show in the main window
            text=True
        )
        return process
    except Exception as e:
        logger.error(f"Failed to start {name}: {e}")
        return None

def main():
    logger.info("==========================================")
    logger.info("   RI2CH ENGINE - MASTER DEPLOYMENT      ")
    logger.info("==========================================")
    
    # 1. Start Webhook Handler (Flask)
    webhook = start_process("Webhook Handler", "webhook_handler.py")
    
    # 2. Start Follow-up Worker
    worker = start_process("Follow-up Worker", "follow_up_worker.py")
    
    # 3. Start Public Bridge (Ngrok)
    tunnel = start_process("Ngrok Tunnel", "start_tunnel.py")
    
    logger.info("All systems initiated.")
    logger.info("Check ngrok output for your Public Webhook URL.")
    logger.info("Press Ctrl+C to terminate all services.")
    
    try:
        while True:
            # Monitor processes
            if webhook.poll() is not None:
                logger.warning("Webhook Handler exited unexpectedly!")
            if worker.poll() is not None:
                logger.warning("Follow-up Worker exited unexpectedly!")
            if tunnel.poll() is not None:
                logger.warning("Ngrok Tunnel exited unexpectedly!")
            
            time.sleep(5)
    except KeyboardInterrupt:
        logger.info("Shutting down RI2CH Engine...")
        webhook.terminate()
        worker.terminate()
        tunnel.terminate()
        logger.info("Cleanup complete.")

if __name__ == "__main__":
    main()
