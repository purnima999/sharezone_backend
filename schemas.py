from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    username: str
    password: str


class CreateZone(BaseModel):
    roomname: str
    email: EmailStr


class Zone(BaseModel):
    id: int
    roomname: str
    email: EmailStr

    class Config:
        orm_mode = True
