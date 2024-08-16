from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    rooms = relationship("Room", back_populates="user")


class Room(Base):
    __tablename__ = "zonerooms"

    id = Column(Integer, primary_key=True, index=True)
    roomname = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), ForeignKey("users.email"), nullable=False)

    user = relationship("User", back_populates="rooms")

    
