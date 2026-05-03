import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import operations

def test_add():
    assert operations.perform_calculation("add", 1, 2) == 3

def test_subtract():
    assert operations.perform_calculation("subtract", 10, 4) == 6

def test_multiply():
    assert operations.perform_calculation("multiply", 3, 3) == 9

def test_divide():
    assert operations.perform_calculation("divide", 10, 2) == 5

def test_divide_by_zero():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        operations.perform_calculation("divide", 10, 0)

def test_exponent():
    assert operations.perform_calculation("exponent", 2, 3) == 8

def test_modulus():
    assert operations.perform_calculation("modulus", 10, 3) == 1

def test_unknown_op():
    with pytest.raises(ValueError, match="Unknown operation"):
        operations.perform_calculation("invalid", 1, 1)

def test_update_user_logic():
    """Unit: Test update_user logic directly using a mock DB."""
    from unittest.mock import MagicMock
    from app.crud import update_user
    from app.schemas import UserUpdate
    from app.models import User
    
    db = MagicMock()
    mock_user = User(id=1, username="test", email="old@test.com", hashed_password="old")
    db.query().filter().first.return_value = mock_user
    
    update_data = UserUpdate(email="new@test.com", password="new_password")
    updated = update_user(db, 1, update_data)
    
    assert updated.email == "new@test.com"
    assert updated.hashed_password != "old"
    assert db.commit.called
