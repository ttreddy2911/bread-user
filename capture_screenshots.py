import os
import sys
import time
import subprocess
import requests
from playwright.sync_api import sync_playwright

# Configuration
PORT = 8002
BASE_URL = f"http://127.0.0.1:{PORT}"
SCREENSHOT_DIR = os.path.join(os.getcwd(), "screenshots")
DB_PATH = "screenshot_test.db"

def start_server():
    print(f"Starting server on port {PORT}...")
    env = os.environ.copy()
    env["SQLALCHEMY_DATABASE_URL"] = f"sqlite:///./{DB_PATH}"
    # Start the FastAPI server using uvicorn as a subprocess
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(PORT)],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for the server to be ready
    for _ in range(20):
        try:
            response = requests.get(BASE_URL)
            if response.status_code == 200:
                print("Server is up and running!")
                return process
        except requests.exceptions.ConnectionError:
            time.sleep(0.5)
            
    print("Failed to start server.")
    process.terminate()
    sys.exit(1)

def capture_screenshots():
    if not os.path.exists(SCREENSHOT_DIR):
        os.makedirs(SCREENSHOT_DIR)
        print(f"Created directory: {SCREENSHOT_DIR}")

    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()

        print("Capturing Login Page...")
        page.goto(BASE_URL)
        page.wait_for_selector("#auth-screen")
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "01_login_page.png"))

        print("Capturing Registration Page...")
        page.click("#tab-register")
        page.wait_for_selector("#reg-form")
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "02_registration_page.png"))

        print("Registering test user...")
        page.fill("#reg-username", "demo_user")
        page.fill("#reg-email", "demo@example.com")
        page.fill("#reg-password", "DemoPass123!")
        page.click("#register-btn")
        time.sleep(1) # Wait for registration to process

        print("Logging in...")
        page.click("#tab-login")
        page.fill("#login-username", "demo_user")
        page.fill("#login-password", "DemoPass123!")
        page.click("#login-btn")
        
        print("Capturing Dashboard (Empty)...")
        page.wait_for_selector("#dashboard")
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "03_dashboard_empty.png"))

        print("Adding a sample calculation...")
        page.fill("#operand1", "42")
        page.select_option("#operation", "multiply")
        page.fill("#operand2", "10")
        page.click("#submit-btn")
        time.sleep(1) # Wait for data to update

        print("Capturing Dashboard (With Data)...")
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "04_dashboard_with_data.png"))

        print("All screenshots captured successfully!")
        browser.close()

if __name__ == "__main__":
    # Clean up old database if exists
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        
    server_process = start_server()
    try:
        capture_screenshots()
    finally:
        print("Shutting down server...")
        server_process.terminate()
        server_process.wait()
        # Clean up database
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
