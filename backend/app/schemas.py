from pydantic import BaseModel
from typing import List, Optional, Dict, Tuple
from datetime import datetime
import enum
from .document_classifier import DocumentType

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
    category: Optional[str] = "food"
    match_score: Optional[int] = None
    co2_per_unit: Optional[float] = None

class ReceiptBase(BaseModel):
    id: int
    user_id: int
    total_footprint: float
    document_type: DocumentType = DocumentType.GROCERY
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


# ============================================================================
# CARBON BUDGETING AI SCHEMAS
# ============================================================================

class CategoryAnalysisSchema(BaseModel):
    """Emission breakdown by category"""
    category: str
    total_kg: float
    percentage: float
    item_count: int
    avg_per_item: float


class CarbonInsightsResponse(BaseModel):
    """Response for /api/carbon/insights"""
    summary: str
    total_footprint_kg: float
    period: str
    average_daily_kg: float
    category_breakdown: List[CategoryAnalysisSchema]
    top_5_sources: List[Dict]
    recurring_patterns: List[Dict]


class ForecastDataSchema(BaseModel):
    """Single day forecast"""
    date: str
    predicted_kg: float
    confidence_interval: Tuple[float, float]
    trend: str


class CarbonForecastResponse(BaseModel):
    """Response for /api/carbon/forecast"""
    forecast_days: int
    forecasts: List[ForecastDataSchema]
    summary: str
    risk_level: str  # low, medium, high


class SimulationChangeRequest(BaseModel):
    """Request for /api/carbon/simulate"""
    change_type: str  # "diet", "commute", "shopping", "energy"
    parameters: Dict


class SimulationResultSchema(BaseModel):
    """Result of simulation"""
    change_description: str
    estimated_reduction_kg: float
    estimated_reduction_percent: float
    annual_impact_kg: float
    affected_categories: List[str]


class TradeoffSuggestionSchema(BaseModel):
    """Practical tradeoff suggestion"""
    suggestion: str


class WeeklyCarbonBudgetSchema(BaseModel):
    """Response for /api/carbon/coach"""
    week_start_date: str
    week_end_date: str
    recommended_weekly_limit_kg: float
    recommended_daily_limit_kg: float
    historical_weekly_avg: float
    progress_percent: Optional[float]
    tradeoff_suggestions: List[str]


class RecipeSuggestionSchema(BaseModel):
    """Low-carbon recipe"""
    name: str
    carbon_footprint_kg: float
    protein_g: float
    prep_time_minutes: int
    ingredients: List[str]
    savings_vs_typical_kg: float


class CommuteOptionSchema(BaseModel):
    """Alternative commute option"""
    mode: str
    annual_carbon_kg: float
    cost_per_month: float
    time_per_day_minutes: int
    feasibility_score: float


class SubscriptionToReplaceSchema(BaseModel):
    """Recurring purchase to replace"""
    item_name: str
    frequency: str
    annual_carbon_kg: float
    alternative: str
    potential_savings_kg: float


class DailyPlanActionSchema(BaseModel):
    """Single day's action"""
    day: int
    focus_area: str
    action: str
    carbon_saved_vs_typical_kg: Optional[float]
    difficulty_level: str


class ThirtyDayPlanSchema(BaseModel):
    """Response for /api/carbon/plan/30-day"""
    start_date: str
    end_date: str
    current_weekly_avg_kg: float
    target_weekly_avg_kg: float
    total_potential_savings_kg: float
    summary: str
    problem_areas: List[CategoryAnalysisSchema]
    improvement_checklist: List[str]
    recipes: List[RecipeSuggestionSchema]
    commute_alternatives: List[CommuteOptionSchema]
    habit_changes: List[str]
    subscriptions_to_replace: List[SubscriptionToReplaceSchema]
    daily_plan: List[DailyPlanActionSchema]
