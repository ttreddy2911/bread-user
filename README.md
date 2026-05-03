# CalcBREAD: Premium Calculation & User Management System

A full-stack web application built with **FastAPI**, **SQLAlchemy**, and **Vanilla JavaScript**. This project implements a secure, JWT-authenticated calculation manager with real-time usage statistics and user profile management.

## 🚀 Quick Start (Local Setup)

### 1. Environment Setup
```powershell
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
playwright install chromium
```

### 2. Launch the Application
```powershell
uvicorn app.main:app --reload
```
Access the UI at: `http://localhost:8000`  
Access API Docs at: `http://localhost:8000/docs`

---

## ✨ Features Deep-Dive

### 1. Secure BREAD Operations (Calculations)
- **Browse**: View all your historical calculations in a glassmorphic table.
- **Read**: Fetch specific calculation details via secure API endpoints.
- **Edit**: Update previous operands or operations; results are automatically re-calculated.
- **Add**: Perform complex math operations with instant database persistence.
- **Delete**: Safely remove records from your history.

### 2. Advanced Operations
- Standard: `+`, `-`, `×`, `÷`
- Advanced: `^` (Exponentiation) and `%` (Modulus).

### 3. Usage Statistics Dashboard (New Feature)
- **Real-time Insights**: Tracks total calculations performed.
- **Data Aggregation**: Calculates the average result across all your math history.
- **Operation Popularity**: Identifies which math operation you use most frequently.
- **Activity Tracking**: Shows the exact timestamp of your last calculation.

### 4. User Profile & Security
- **JWT Authentication**: Secure login/registration using encrypted tokens.
- **Password Hashing**: Uses `bcrypt` for industry-standard security.
- **Profile Management**: Update your email or change your password directly from the "Settings" menu.

---

## 🧪 Testing Strategy (16 Tests)

We implemented a multi-layered testing strategy to ensure 100% reliability. **To run all tests, use:** `pytest tests/ -v`

### 1. Unit Tests (`tests/test_unit.py`)
Focuses on pure logic without requiring a database or network.
- `test_add/sub/mul/div`: Verified basic arithmetic precision.
- `test_divide_by_zero`: Ensured the system handles math errors gracefully.
- `test_exponent/modulus`: Validated the new advanced math operations.
- `test_update_user_logic`: Verified the logic for updating user emails and passwords.

### 2. Integration Tests (`tests/test_integration.py`)
Verifies the communication between FastAPI routes and the SQLite database.
- `test_register_and_login`: Confirms users are saved and can authenticate.
- `test_calculations_crud_and_stats`: Verifies that adding a calculation correctly updates the statistics database.
- `test_update_profile_api`: Ensures the API correctly modifies user records and re-hashes new passwords.

### 3. E2E Tests (`tests/test_e2e.py`)
Simulates real user behavior in a Chromium browser using Playwright.
- `test_full_bread_with_stats`: A full journey (Register -> Login -> Create -> Edit -> Delete -> Check Stats).
- `test_password_change`: Navigates to Settings, changes the password, logs out, and verifies the new password works for login.
- `test_unauthorized_access`: Confirms that the dashboard is hidden from users who aren't logged in.
- `test_divide_by_zero_ui`: Verifies that the frontend shows a red error message when a user tries illegal math.

---

## 📸 Documentation Requirements

Save the following screenshots in the `screenshots/` folder:

1.  **`FastAPI_UI.png`**: The main Dashboard with a few calculations in the table.
2.  **`Profile_UI.png`**: The Profile Settings screen open.
3.  **`SwaggerUI.png`**: The `/docs` page showing all routes (including `PUT /api/users/me`).
4.  **`Tests.png`**: The terminal showing `16 passed` after running `pytest`.
5.  **`browse_read.png`**: The Calculation History table.
6.  **`error.png`**: The UI showing a "Cannot divide by zero" error.
7.  **`GitHubActions.png`**: Your "Actions" tab on GitHub (Green).
8.  **`DockerHub.png`**: Your repository on Docker Hub.

---

## 🐳 Docker Deployment
```bash
docker build -t tippireddy/calc-bread .
docker run -p 8000:8000 tippireddy/calc-bread
```
