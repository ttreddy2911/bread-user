import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Set up test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./integration_test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from app.main import app
from app.database import Base, get_db

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def test_register_and_login():
    # Register
    res = client.post("/api/register", json={"username": "int_user", "email": "int@test.com", "password": "password"})
    assert res.status_code == 201
    
    # Login
    res = client.post("/api/login", data={"username": "int_user", "password": "password"})
    assert res.status_code == 200
    assert "access_token" in res.json()

def test_calculations_crud_and_stats():
    # Setup Auth
    client.post("/api/register", json={"username": "user1", "email": "u1@test.com", "password": "p1"})
    login_res = client.post("/api/login", data={"username": "user1", "password": "p1"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # ADD
    client.post("/api/calculations", json={"operation": "add", "operand1": 10, "operand2": 10}, headers=headers)
    client.post("/api/calculations", json={"operation": "multiply", "operand1": 5, "operand2": 2}, headers=headers)
    
    # BROWSE
    res = client.get("/api/calculations", headers=headers)
    assert len(res.json()) == 2
    
    # STATS (NEW FEATURE)
    stats_res = client.get("/api/reports/stats", headers=headers)
    stats = stats_res.json()
    assert stats["total_count"] == 2
    assert stats["average_result"] == 15.0 # (20 + 10) / 2
    assert stats["operation_counts"]["add"] == 1
    assert stats["operation_counts"]["multiply"] == 1

def test_update_profile_api():
    """Integration: Test the Profile Update API route."""
    user = {"username": "prof_test", "email": "p@test.com", "password": "pass"}
    client.post("/api/register", json=user)
    login_res = client.post("/api/login", data={"username": user["username"], "password": user["password"]})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Update Email
    update_data = {"email": "new@test.com", "password": "new_password"}
    res = client.put("/api/users/me", json=update_data, headers=headers)
    assert res.status_code == 200
    assert res.json()["email"] == "new@test.com"
    
    # Verify Login with new password
    login_res = client.post("/api/login", data={"username": user["username"], "password": "new_password"})
    assert login_res.status_code == 200
