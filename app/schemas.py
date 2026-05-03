from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class User(UserBase):
    id: int
    class Config:
        from_attributes = True

# Calculation Schemas
class CalculationBase(BaseModel):
    operation: str
    operand1: float
    operand2: float

class CalculationCreate(CalculationBase):
    pass

class CalculationUpdate(BaseModel):
    operation: Optional[str] = None
    operand1: Optional[float] = None
    operand2: Optional[float] = None

class Calculation(CalculationBase):
    id: int
    result: float
    timestamp: datetime
    owner_id: int
    class Config:
        from_attributes = True

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Statistics Report Schema (NEW FEATURE)
class StatsReport(BaseModel):
    total_count: int
    operation_counts: dict
    average_result: float
    last_calculation: Optional[datetime] = None
