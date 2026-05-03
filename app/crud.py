from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models, schemas, security, operations

# User CRUD
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return None
    
    if user_update.email:
        db_user.email = user_update.email
    if user_update.password:
        db_user.hashed_password = security.get_password_hash(user_update.password)
    
    db.commit()
    db.refresh(db_user)
    return db_user

# Calculation CRUD
def get_calculations(db: Session, user_id: int):
    return db.query(models.Calculation).filter(models.Calculation.owner_id == user_id).all()

def get_calculation(db: Session, calc_id: int, user_id: int):
    return db.query(models.Calculation).filter(
        models.Calculation.id == calc_id,
        models.Calculation.owner_id == user_id
    ).first()

def create_calculation(db: Session, calculation: schemas.CalculationCreate, user_id: int):
    result = operations.perform_calculation(
        calculation.operation, calculation.operand1, calculation.operand2
    )
    db_calc = models.Calculation(
        **calculation.dict(),
        result=result,
        owner_id=user_id
    )
    db.add(db_calc)
    db.commit()
    db.refresh(db_calc)
    return db_calc

def update_calculation(db: Session, calc_id: int, calculation: schemas.CalculationUpdate, user_id: int):
    db_calc = get_calculation(db, calc_id, user_id)
    if not db_calc:
        return None
    
    update_data = calculation.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_calc, key, value)
    
    # Recalculate result
    db_calc.result = operations.perform_calculation(
        db_calc.operation, db_calc.operand1, db_calc.operand2
    )
    
    db.commit()
    db.refresh(db_calc)
    return db_calc

def delete_calculation(db: Session, calc_id: int, user_id: int):
    db_calc = get_calculation(db, calc_id, user_id)
    if db_calc:
        db.delete(db_calc)
        db.commit()
        return True
    return False

# NEW FEATURE: Statistics Report Logic
def get_stats(db: Session, user_id: int):
    calcs = db.query(models.Calculation).filter(models.Calculation.owner_id == user_id).all()
    if not calcs:
        return {
            "total_count": 0,
            "operation_counts": {},
            "average_result": 0.0,
            "last_calculation": None
        }
    
    total_count = len(calcs)
    op_counts = {}
    total_result = 0.0
    last_calc = calcs[0].timestamp
    
    for c in calcs:
        op_counts[c.operation] = op_counts.get(c.operation, 0) + 1
        total_result += c.result
        if c.timestamp > last_calc:
            last_calc = c.timestamp
            
    return {
        "total_count": total_count,
        "operation_counts": op_counts,
        "average_result": round(total_result / total_count, 2),
        "last_calculation": last_calc
    }
