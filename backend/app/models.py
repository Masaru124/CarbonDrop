from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum
from .document_classifier import DocumentType

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    eco_credits = Column(Integer, default=0)

    receipts = relationship("Receipt", back_populates="owner")

class Receipt(Base):
    __tablename__ = "receipts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_footprint = Column(Float)
    document_type = Column(String, default="grocery")
    date = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="receipts")
    items = relationship("Item", back_populates="receipt")

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    receipt_id = Column(Integer, ForeignKey("receipts.id"))
    name = Column(String)
    matched_name = Column(String)
    qty = Column(Float)
    unit = Column(String)
    footprint = Column(Float)
    category = Column(String, default="food")  # food, transport, energy, utility, etc.
    match_score = Column(Integer, nullable=True)  # Fuzzy matching score (0-100)
    co2_per_unit = Column(Float, nullable=True)  # CO2 emissions per unit

    receipt = relationship("Receipt", back_populates="items")

class UserOffset(Base):
    __tablename__ = "user_offsets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    trees_planted = Column(Integer)
    co2_offset_kg = Column(Float)
    date = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User")


# ============================================================================
# CARBON BUDGETING AI MODELS
# ============================================================================

class CarbonGoal(Base):
    """User's current carbon reduction goal"""
    __tablename__ = "carbon_goals"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    weekly_limit_kg = Column(Float)
    daily_limit_kg = Column(Float)
    reduction_target_percent = Column(Float, default=15.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User")


class SustainabilityPlan(Base):
    """30-day personalized sustainability plan"""
    __tablename__ = "sustainability_plans"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    current_weekly_avg_kg = Column(Float)
    target_weekly_avg_kg = Column(Float)
    total_potential_savings_kg = Column(Float)
    summary = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User")


class DailyPlanAction(Base):
    """Daily action item in sustainability plan"""
    __tablename__ = "daily_plan_actions"
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("sustainability_plans.id"))
    day = Column(Integer)
    focus_area = Column(String)
    action = Column(String)
    carbon_saved_kg = Column(Float, nullable=True)
    difficulty_level = Column(String)  # easy, medium, hard
    completed = Column(Integer, default=0)  # Boolean flag

    plan = relationship("SustainabilityPlan")
