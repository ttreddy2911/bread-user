from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from . import models, schemas, crud, security, database

# Initialize DB tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Calculation BREAD API")

# Security setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

def get_current_user(db: Session = Depends(database.get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = security.jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except security.JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# --- AUTH ROUTES ---

@app.post("/api/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@app.post("/api/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- BREAD ROUTES (Calculations) ---

@app.get("/api/calculations", response_model=List[schemas.Calculation])
def browse_calculations(current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    return crud.get_calculations(db, user_id=current_user.id)

@app.get("/api/calculations/{calc_id}", response_model=schemas.Calculation)
def read_calculation(calc_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    db_calc = crud.get_calculation(db, calc_id=calc_id, user_id=current_user.id)
    if db_calc is None:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return db_calc

@app.post("/api/calculations", response_model=schemas.Calculation, status_code=status.HTTP_201_CREATED)
def add_calculation(calculation: schemas.CalculationCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    try:
        return crud.create_calculation(db, calculation=calculation, user_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/calculations/{calc_id}", response_model=schemas.Calculation)
def edit_calculation(calc_id: int, calculation: schemas.CalculationUpdate, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    try:
        db_calc = crud.update_calculation(db, calc_id=calc_id, calculation=calculation, user_id=current_user.id)
        if db_calc is None:
            raise HTTPException(status_code=404, detail="Calculation not found")
        return db_calc
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/calculations/{calc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calculation(calc_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    success = crud.delete_calculation(db, calc_id=calc_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return None

# --- NEW FEATURE: REPORT ROUTE ---

@app.get("/api/reports/stats", response_model=schemas.StatsReport)
def get_usage_stats(current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    return crud.get_stats(db, user_id=current_user.id)

# --- USER PROFILE ROUTES ---

@app.put("/api/users/me", response_model=schemas.User)
def update_profile(user_update: schemas.UserUpdate, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    updated_user = crud.update_user(db, user_id=current_user.id, user_update=user_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

# Serve Frontend
app.mount("/", StaticFiles(directory="static", html=True), name="static")
