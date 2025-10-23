from pydantic import BaseModel
from typing import List
from datetime import datetime

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
    eco_credits: int

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
    date: datetime

# ------------------
# Dashboard & Leaderboard
# ------------------
class DashboardEntry(BaseModel):
    month: str
    total: float

class LeaderboardEntry(BaseModel):
    username: str
    score: float

# ------------------
# Simulation schemas
# ------------------
class EnergyEfficiencyRequest(BaseModel):
    current_bulbs: int
    led_bulbs: int
    hours_per_day: int = 4
    days_per_year: int = 365

class ElectricVehicleRequest(BaseModel):
    annual_km: int
    current_fuel_efficiency: float = 10
    ev_efficiency: float = 0.2

class LocalFoodRequest(BaseModel):
    imported_meals_per_week: int
    local_reduction_percent: int = 50
    weeks: int = 52

class WasteReductionRequest(BaseModel):
    current_waste_kg_per_week: float
    reduction_percent: int = 30
    weeks: int = 52

class MeatReplacementRequest(BaseModel):
    meat_meals_per_week: int
    weeks: int = 52

class TransportSwitchRequest(BaseModel):
    trips_per_year: int
    distance_per_trip_km: float
    from_mode: str = "flight"
    to_mode: str = "train"
