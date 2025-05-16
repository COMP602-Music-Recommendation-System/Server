from datetime import timedelta
import logging

from fastapi import Depends, FastAPI, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.session import get_db, engine
from app import models
from app.models import User
from app.schemas import Token, UserCreate, UserResponse  # TokenData removed as it's not used

from app.auth.utils import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    create_access_token,
    get_current_user,
    get_password_hash
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Music App API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
try:
    models.Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
except Exception as db_error:
    logger.error(f"Error creating database tables: {db_error}")

@app.exception_handler(Exception)
async def global_exception_handler(exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please check the logs for more details."},
    )

@app.post("/token", response_model=Token, tags=["authentication"])
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=UserResponse, tags=["users"])
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/me/", response_model=UserResponse, tags=["users"])
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/", response_class=HTMLResponse, tags=["home"])
async def root():
    return """
    <html>
        <head><title>Music App API</title></head>
        <body>
            <h1>Welcome to the Music App API</h1>
            <p>This API provides endpoints for user authentication and management.</p>
            <a href="/docs">Go to Swagger Documentation</a>
        </body>
    </html>
    """

@app.post("/login-tests", tags=["authentication"])
async def login_test(username: str = Form(...), password: str = Form(...)):
    return {
        "username": username,
        "password_length": len(password),
        "message": "This is a test endpoint to verify form data processing"
    }
