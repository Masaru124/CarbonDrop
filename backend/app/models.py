from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

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

    receipt = relationship("Receipt", back_populates="items")

class UserOffset(Base):
    __tablename__ = "user_offsets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    trees_planted = Column(Integer)
    co2_offset_kg = Column(Float)
    date = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User")
