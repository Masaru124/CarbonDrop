from pydantic import BaseModel
from typing import List

# ------------------
# User schemas
# ------------------
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserLogin(UserBase):
    password: str

class UserOut(UserBase):
    id: int

# ------------------
# Receipt / Item schemas
# ------------------
class ItemBase(BaseModel):
    name: str
    matched_name: str
    qty: float
    unit: str
    footprint: float

class ReceiptBase(BaseModel):
    id: int
    user_id: int
    total_footprint: float
    items: List[ItemBase]

# ------------------
# Dashboard & Leaderboard
# ------------------
class DashboardEntry(BaseModel):
    month: str
    total: float

class LeaderboardEntry(BaseModel):
    username: str
    score: float
