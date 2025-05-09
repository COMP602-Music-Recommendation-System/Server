from datetime import timedelta
import logging
from typing import List

from fastapi import Depends, FastAPI, HTTPException, status, Form, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.db.session import get_db, engine
from app.db import models
from app.db.models import UserModel, User, UserCreate, Token

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

# Create FastAPI app
app = FastAPI(
    title="Music App API",
    description="API for a music application with user authentication",
    version="1.0.0",
)

# Enable CORS
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
except Exception as e:
    logger.error(f"Error creating database tables: {e}")


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
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
    logger.info(f"Login attempt for user: {form_data.username}")
    try:
        user = authenticate_user(db, form_data.username, form_data.password)
        if not user:
            logger.warning(f"Failed login attempt for user: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        logger.info(f"Successful login for user: {form_data.username}")
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"Error in login process: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during authentication"
        )


@app.post("/users/", response_model=User, tags=["users"])
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Attempting to create user: {user.username}")
    try:
        # Check if username already exists
        db_user = db.query(UserModel).filter(UserModel.username == user.username).first()
        if db_user:
            logger.warning(f"Username already exists: {user.username}")
            raise HTTPException(status_code=400, detail="Username already registered")

        # Check if email already exists
        db_user = db.query(UserModel).filter(UserModel.email == user.email).first()
        if db_user:
            logger.warning(f"Email already exists: {user.email}")
            raise HTTPException(status_code=400, detail="Email already registered")

        # Create the user with hashed password
        try:
            hashed_password = get_password_hash(user.password)
        except Exception as e:
            logger.error(f"Error hashing password: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="Error processing password. Please try again."
            )

        db_user = UserModel(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"User created successfully: {user.username}")
        return db_user
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while creating the user"
        )


@app.get("/users/me/", response_model=User, tags=["users"])
async def read_users_me(current_user: UserModel = Depends(get_current_user)):
    logger.info(f"User {current_user.username} accessed their profile")
    return current_user


@app.get("/", response_class=HTMLResponse, tags=["home"])
async def root():
    return """
    <html>
        <head>
            <title>Music App API</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 40px;
                    line-height: 1.6;
                }
                h1 {
                    color: #333;
                }
                .btn {
                    display: inline-block;
                    background: #4CAF50;
                    color: white;
                    padding: 10px 20px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin-top: 20px;
                }
            </style>
        </head>
        <body>
            <h1>Welcome to the Music App API</h1>
            <p>This API provides endpoints for user authentication and management.</p>
            <p>Visit <a href="/docs" class="btn">API Documentation</a> to interact with the API.</p>
        </body>
    </html>
    """


# Alternative login endpoint for debugging
@app.post("/login-test", tags=["authentication"])
async def login_test(
        username: str = Form(...),
        password: str = Form(...)
):
    logger.info(f"Test login attempt for: {username}")
    return {
        "username": username,
        "password_length": len(password),
        "message": "This is a test endpoint to verify form data processing"
    }