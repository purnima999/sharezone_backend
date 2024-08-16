from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models
import schemas
import zone
from database import SessionLocal, engine, Base
from fastapi.middleware.cors import CORSMiddleware
from typing import List

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:3001",
    # "http://your-frontend-domain.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods like GET, POST, etc.
    allow_headers=["*"],  # Allow all headers
)

# Create the database tables
Base.metadata.create_all(bind=engine)

# Dependency to get the DB session


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/register/", status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = zone.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    db_user = zone.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    new_user = zone.create_user(db=db, user=user)

    return {
        "status": True,
        "statuscode": status.HTTP_201_CREATED,
        "message": "User created successfully",
        # "data": new_user  # Optionally include the new user object
    }


@app.post("/login/", status_code=status.HTTP_200_OK)
def login_user(login_data: schemas.UserLogin, db: Session = Depends(get_db)):
    # Authenticate the user
    user = zone.authenticate_user(
        db, username=login_data.username, password=login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid credentials"
        )

    return {
        "status": True,
        "statuscode": status.HTTP_200_OK,
        "message": "Login successful",
        "data": user
    }


@app.post("/create_zone/", status_code=status.HTTP_201_CREATED)
def create_zone(zone: schemas.CreateZone, db: Session = Depends(get_db)):

    # Check if the room name already exists
    db_zone = db.query(models.Room).filter(models.Room.roomname == zone.roomname).first()
    if db_zone:
        return {
            "status": False,
            "statuscode": status.HTTP_400_BAD_REQUEST,
            "message": "Room name already exists"
        }

    # Check if the email exists in the users table
    db_user = db.query(models.User).filter(models.User.email == zone.email).first()
    if not db_user:
        return {
            "status": False,
            "statuscode": status.HTTP_400_BAD_REQUEST,
            "message": "User with this email does not exist"
        }

    # Create the zone
    try:
        new_zone = models.Room(roomname=zone.roomname, email=zone.email)
        db.add(new_zone)
        db.commit()
        db.refresh(new_zone)

        return {
            "status": True,
            "statuscode": status.HTTP_201_CREATED,
            "message": "Zone created successfully",
            # "data": new_zone
        }
    except Exception as e:
        # Handle any unexpected errors
        return {
            "status": False,
            "statuscode": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": f"An error occurred while creating the zone: {str(e)}"
        }

@app.get("/get_zones/{email}/", status_code=status.HTTP_200_OK)
def get_zones(email: str, db: Session = Depends(get_db)):
    zones = zone.get_zones_by_email(db, email=email)
    if not zones:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No zones found for this email"
        )
    return {
        "status": True,
        "statuscode": status.HTTP_200_OK,
        "message": "Zones retrieved successfully",
        "data": zones
    }