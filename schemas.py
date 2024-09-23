from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str
    password: str

class FlowerCreate(BaseModel):
    name: str
    price: float

class PurchaseCreate(BaseModel):
    user_id: int
    flower_id: int
