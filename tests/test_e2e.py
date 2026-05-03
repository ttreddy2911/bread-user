import pytest
from playwright.sync_api import Page, expect
import multiprocessing
import uvicorn
import time
import requests
import os
import sys
from re import compile

def run_server():
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    os.environ["SQLALCHEMY_DATABASE_URL"] = "sqlite:///./test_calculations.db"
    from app.main import app
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="error")

@pytest.fixture(scope="session", autouse=True)
def server():
    if os.path.exists("test_calculations.db"):
        try: os.remove("test_calculations.db")
        except: pass
    
    proc = multiprocessing.Process(target=run_server, daemon=True)
    proc.start()
    
    # Wait for server
    for _ in range(20):
        try:
            res = requests.get("http://127.0.0.1:8001/")
            if res.status_code == 200: break
        except:
            time.sleep(0.5)
    
    yield
    proc.terminate()
    proc.join()
    if os.path.exists("test_calculations.db"):
        try: os.remove("test_calculations.db")
        except: pass

BASE = "http://127.0.0.1:8001"
TEST_USER = {"username": "testuser", "email": "test@test.com", "password": "Password123"}

def test_full_bread_with_stats(page: Page):
    """E2E: Register, Login, BREAD cycle and verify Statistics update."""
    page.goto(BASE)
    
    # Register
    page.click("#tab-register")
    page.fill("#reg-username", TEST_USER["username"])
    page.fill("#reg-email", TEST_USER["email"])
    page.fill("#reg-password", TEST_USER["password"])
    page.click("#register-btn")
    
    # Wait for success message
    expect(page.locator("#register-error")).to_contain_text("Account created")
    
    # Login
    page.click("#tab-login")
    page.fill("#login-username", TEST_USER["username"])
    page.fill("#login-password", TEST_USER["password"])
    page.click("#login-btn")
    
    # Wait for dashboard
    expect(page.locator("#dashboard")).to_be_visible()
    
    # Initial Stats Check
    expect(page.locator("#stat-total")).to_have_text(compile(r"0"))
    
    # ADD (10 + 5 = 15)
    page.fill("#operand1", "10")
    page.select_option("#operation", "add")
    page.fill("#operand2", "5")
    page.click("#submit-btn")
    
    # Verify Stats Updated
    expect(page.locator("#stat-total")).to_have_text(compile(r"1"))
    expect(page.locator("#stat-avg")).to_have_text(compile(r"15"))
    
    # EDIT (Change to 10 * 5 = 50)
    page.click("button:text('Edit')")
    
    # Wait for the form to actually load the edit mode
    expect(page.locator("#submit-btn")).to_have_text("Update")
    
    page.select_option("#operation", "multiply")
    page.click("#submit-btn")
    
    # Wait for the table to reflect the new result first
    expect(page.locator("#calc-tbody tr").first.locator("td:nth-child(5)")).to_have_text("50")
    
    # Verify Stats After Edit
    expect(page.locator("#stat-avg")).to_have_text(compile(r"50"))
    
    # DELETE
    page.once("dialog", lambda d: d.accept())
    page.click("button:text('Delete')")
    expect(page.locator("#calc-tbody")).to_contain_text("No calculations yet")
    expect(page.locator("#stat-total")).to_have_text(compile(r"0"))

def test_unauthorized_access(page: Page):
    """Negative: Accessing dashboard without login."""
    page.goto(BASE)
    expect(page.locator("#auth-screen")).to_be_visible()
    expect(page.locator("#dashboard")).to_have_class(compile("hidden"))

def test_divide_by_zero(page: Page):
    """Negative: Error handling for division by zero."""
    # Ensure user exists for login
    requests.post(f"{BASE}/api/register", json=TEST_USER)
    
    page.goto(BASE)
    page.fill("#login-username", TEST_USER["username"])
    page.fill("#login-password", TEST_USER["password"])
    page.click("#login-btn")
    
    page.fill("#operand1", "10")
    page.select_option("#operation", "divide")
    page.fill("#operand2", "0")
    page.click("#submit-btn")
    
    expect(page.locator("#form-message")).to_contain_text("Cannot divide by zero")

def test_password_change(page: Page):
    """E2E: Update email and change password, then verify re-login works."""
    # Register and Login
    user = {"username": "prof_user", "email": "p@p.com", "password": "old_password"}
    requests.post(f"{BASE}/api/register", json=user)
    
    page.goto(BASE)
    page.fill("#login-username", user["username"])
    page.fill("#login-password", user["password"])
    page.click("#login-btn")
    
    # Open Profile Settings
    page.click("#profile-btn")
    expect(page.locator("#profile-section")).to_be_visible()
    
    # Change Email and Password
    new_email = "new@new.com"
    new_password = "new_password"
    page.fill("#prof-email", new_email)
    page.fill("#prof-password", new_password)
    page.click("button:text('Save Changes')")
    
    # Wait for logout (after 2s)
    page.wait_for_selector("#auth-screen", state="visible", timeout=10000)
    
    # Try Login with NEW password
    page.fill("#login-username", user["username"])
    page.fill("#login-password", new_password)
    page.click("#login-btn")
    
    # Verify Dashboard Access
    expect(page.locator("#dashboard")).to_be_visible()
