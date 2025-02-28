import os
import subprocess
import sys
import time
import webbrowser
import logging
import psutil
import signal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("system.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("thomas_system")

# Configuration
API_PORT = 8002
STREAMLIT_PORT = 8003
API_URL = f"http://localhost:{API_PORT}"
DASHBOARD_URL = f"http://localhost:{STREAMLIT_PORT}"

def initialize_database():
    """Initialize the database if it doesn't exist"""
    logger.info("Initializing database...")
    result = subprocess.run([sys.executable, "init_db.py"], 
                           cwd=os.path.dirname(os.path.abspath(__file__)),
                           capture_output=True, text=True)
    if result.returncode == 0:
        logger.info("Database initialized successfully")
        return True
    else:
        logger.error(f"Database initialization failed: {result.stderr}")
        return False

def kill_existing_processes():
    """Kill any existing API or Streamlit processes"""
    logger.info("Checking for existing processes...")
    killed = 0
    
    # Check for Python processes running API or Streamlit
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
            if ('api/main.py' in cmdline or 
                'uvicorn' in cmdline and f'--port={API_PORT}' in cmdline or
                'streamlit run' in cmdline and f'--server.port={STREAMLIT_PORT}' in cmdline):
                logger.info(f"Killing process {proc.info['pid']}: {cmdline}")
                os.kill(proc.info['pid'], signal.SIGTERM)
                killed += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    if killed > 0:
        logger.info(f"Killed {killed} existing processes")
        time.sleep(2)  # Give processes time to terminate
    else:
        logger.info("No existing processes found")
    
    return killed

def start_api_server():
    """Start the API server with proper error handling"""
    logger.info(f"Starting API server on port {API_PORT}...")
    try:
        api_process = subprocess.Popen(
            [sys.executable, "api/main.py", f"--port={API_PORT}"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True
        )
        
        # Wait briefly and check if process is still running
        time.sleep(3)
        if api_process.poll() is not None:
            stdout, stderr = api_process.communicate()
            logger.error(f"API server failed to start: {stderr}")
            return None
        
        logger.info(f"API server started with PID: {api_process.pid}")
        return api_process
    except Exception as e:
        logger.error(f"Failed to start API server: {str(e)}")
        return None

def start_dashboard():
    """Start the Streamlit dashboard with proper error handling"""
    logger.info(f"Starting Streamlit dashboard on port {STREAMLIT_PORT}...")
    try:
        dashboard_process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "ui/dashboard.py", 
             f"--server.port={STREAMLIT_PORT}", "--server.address=0.0.0.0"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True
        )
        
        # Wait briefly and check if process is still running
        time.sleep(3)
        if dashboard_process.poll() is not None:
            stdout, stderr = dashboard_process.communicate()
            logger.error(f"Streamlit dashboard failed to start: {stderr}")
            return None
        
        logger.info(f"Streamlit dashboard started with PID: {dashboard_process.pid}")
        return dashboard_process
    except Exception as e:
        logger.error(f"Failed to start Streamlit dashboard: {str(e)}")
        return None

def open_browser():
    """Open the dashboard in the user's browser"""
    # Wait a moment for servers to start
    time.sleep(5)
    logger.info(f"Opening dashboard in browser: {DASHBOARD_URL}")
    try:
        webbrowser.open(DASHBOARD_URL)
    except Exception as e:
        logger.error(f"Failed to open browser: {str(e)}")

def check_api_health():
    """Check if the API server is responding"""
    import requests
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            logger.info("API health check successful")
            return True
    except Exception as e:
        logger.error(f"API health check failed: {str(e)}")
    return False

if __name__ == "__main__":
    logger.info("Starting Thomas AI Management System...")
    
    # Create necessary directories if they don't exist
    os.makedirs("logs", exist_ok=True)
    
    # Kill any existing processes
    kill_existing_processes()
    
    # Initialize the database
    if not initialize_database():
        logger.error("Failed to initialize database. Exiting.")
        sys.exit(1)
    
    # Start the API server
    api_process = start_api_server()
    if not api_process:
        logger.error("Failed to start API server. Exiting.")
        sys.exit(1)
    
    # Start the dashboard
    dashboard_process = start_dashboard()
    if not dashboard_process:
        logger.error("Failed to start dashboard. Killing API server.")
        api_process.terminate()
        sys.exit(1)
    
    # Open browser
    open_browser()
    
    logger.info("\nThomas AI Management System is running!")
    logger.info(f"API server: {API_URL}")
    logger.info(f"API documentation: {API_URL}/docs")
    logger.info(f"Dashboard: {DASHBOARD_URL}")
    logger.info("\nPress Ctrl+C to stop all services...")
    
    try:
        # Keep the script running and periodically check API health
        while True:
            time.sleep(30)
            check_api_health()
    except KeyboardInterrupt:
        logger.info("\nShutting down Thomas AI Management System...")
        api_process.terminate()
        dashboard_process.terminate()
        logger.info("System stopped.")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        api_process.terminate()
        dashboard_process.terminate()
        sys.exit(1) 