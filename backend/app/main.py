import os
import json
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from .ocr import extract_items_from_image
from .footprint import FootprintMatcher, WhatIfSimulator, load_dataset, calculate_offset_from_trees, get_gamification_badge, calculate_trees_needed, calculate_eco_credits, get_credits_needed_for_tree
from .utils import normalize_quantity
from datetime import datetime
from . import auth, report
from . import models, schemas, database

from fastapi import APIRouter

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title='EcoBasket API')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

matcher = FootprintMatcher(load_dataset(database.DATASET_PATH))
simulator = WhatIfSimulator(load_dataset(database.DATASET_PATH))

@app.post('/upload_receipt', response_model=schemas.ReceiptBase)
async def upload_receipt(file: UploadFile = File(...), current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    contents = await file.read()

    try:
        items_raw = extract_items_from_image(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'OCR failed: {e}')

    # Normalize quantities
    items = []
    for it in items_raw:
        qty_kg, _ = normalize_quantity(f"{it.get('qty', 1)} {it.get('name', '')}")
        items.append({'name': it.get('name', ''), 'qty': qty_kg})

    results, total = matcher.match_and_compute(items)

    # Create receipt and items in DB linked to current user
    receipt = models.Receipt(user_id=current_user.id, total_footprint=total, date=datetime.utcnow())
    db.add(receipt)
    db.commit()
    db.refresh(receipt)

    for item in results:
        db_item = models.Item(
            receipt_id=receipt.id,
            name=item['name'],
            matched_name=item['matched_name'],
            qty=item['qty'],
            unit=item['unit'],
            footprint=item['footprint']
        )
        db.add(db_item)
    db.commit()

    # Award EcoCredits for uploading receipt
    credits_earned = calculate_eco_credits(total)
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    user.eco_credits += credits_earned
    db.add(user)
    db.commit()
    db.refresh(user)

    receipt_items = db.query(models.Item).filter(models.Item.receipt_id == receipt.id).all()
    receipt_data = schemas.ReceiptBase(
        id=receipt.id,
        user_id=receipt.user_id,
        total_footprint=receipt.total_footprint,
        items=[schemas.ItemBase(
            name=i.name,
            matched_name=i.matched_name or "",
            qty=i.qty,
            unit=i.unit or "",
            footprint=i.footprint
        ) for i in receipt_items],
        date=receipt.date
    )
    return receipt_data

@app.post('/plant_trees')
def plant_trees(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    """
    Virtual tree planting endpoint - users redeem EcoCredits to plant trees.
    """
    # Get user's total carbon footprint from receipts
    total_footprint = db.query(func.sum(models.Receipt.total_footprint)).filter(
        models.Receipt.user_id == current_user.id
    ).scalar() or 0

    if total_footprint <= 0:
        raise HTTPException(status_code=400, detail="No carbon footprint data found. Please upload receipts first.")

    # Calculate user's current EcoCredits
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    credits_needed = get_credits_needed_for_tree()

    # Calculate how many trees user can plant based on credits
    trees = user.eco_credits // credits_needed
    if trees <= 0:
        raise HTTPException(status_code=400, detail="Insufficient EcoCredits to plant a tree. Earn more credits by reducing your footprint.")

    # Deduct credits for planted trees
    user.eco_credits -= trees * credits_needed
    db.add(user)

    co2_offset = calculate_offset_from_trees(trees)

    user_offset = models.UserOffset(
        user_id=current_user.id,
        trees_planted=trees,
        co2_offset_kg=co2_offset,
        date=datetime.utcnow()
    )
    db.add(user_offset)
    db.commit()
    db.refresh(user_offset)

    badge_info = get_gamification_badge(
        db.query(models.UserOffset).filter(models.UserOffset.user_id == current_user.id).with_entities(
            func.sum(models.UserOffset.trees_planted)
        ).scalar() or 0
    )

    return {
        "message": f"Successfully planted {trees} virtual trees to offset {round(total_footprint, 2)} kg CO₂!",
        "trees_planted": trees,
        "carbon_footprint_offset": round(total_footprint, 2),
        "co2_offset_kg": co2_offset,
        "badge": badge_info,
        "remaining_eco_credits": user.eco_credits
    }

@app.get('/user_offsets')
def get_user_offsets(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    """
    Get user's offset statistics.
    """
    # Get total trees and offset
    total_trees = db.query(func.sum(models.UserOffset.trees_planted)).filter(
        models.UserOffset.user_id == current_user.id
    ).scalar() or 0

    total_offset = db.query(func.sum(models.UserOffset.co2_offset_kg)).filter(
        models.UserOffset.user_id == current_user.id
    ).scalar() or 0

    badge_info = get_gamification_badge(total_trees)

    return {
        "total_trees": int(total_trees),
        "total_offset": round(total_offset, 2),
        "badge": badge_info["badge"],
        "level": badge_info["level"]
    }

@app.get('/footprint_history', response_model=list[schemas.ReceiptBase])
def footprint_history(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    receipts = db.query(models.Receipt).filter(models.Receipt.user_id == current_user.id).order_by(models.Receipt.date.desc()).all()
    result = []
    for receipt in receipts:
        items = db.query(models.Item).filter(models.Item.receipt_id == receipt.id).all()
        receipt_data = schemas.ReceiptBase(
            id=receipt.id,
            user_id=receipt.user_id,
            total_footprint=receipt.total_footprint,
            items=[schemas.ItemBase(
                name=i.name,
                matched_name=i.matched_name or "",
                qty=i.qty,
                unit=i.unit or "",
                footprint=i.footprint
            ) for i in items],
            date=receipt.date
        )
        result.append(receipt_data)
    return result

@app.post('/simulate_meat_replacement')
def simulate_meat_replacement(meat_meals_per_week: int, weeks: int = 52):
    """
    Simulate replacing meat meals with plant-based alternatives.
    """
    try:
        result = simulator.simulate_meat_replacement(meat_meals_per_week, weeks)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post('/simulate_transport_switch')
def simulate_transport_switch(trips_per_year: int, distance_per_trip_km: float, from_mode: str = 'flight', to_mode: str = 'train'):
    """
    Simulate switching from one transport mode to another.
    """
    try:
        result = simulator.simulate_transport_switch(trips_per_year, distance_per_trip_km, from_mode, to_mode)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

dashboard_router = APIRouter()

@dashboard_router.get("/", response_model=list[schemas.DashboardEntry])
def get_dashboard(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    from sqlalchemy import func
    # Get monthly totals for the current user
    monthly_data = db.query(
        func.strftime('%Y-%m', models.Receipt.date).label('month'),
        func.sum(models.Receipt.total_footprint).label('total')
    ).filter(models.Receipt.user_id == current_user.id).group_by(func.strftime('%Y-%m', models.Receipt.date)).all()

    return [{"month": m.month, "total": round(m.total, 2)} for m in monthly_data]

leaderboard_router = APIRouter()

@leaderboard_router.get("/", response_model=list[schemas.LeaderboardEntry])
def get_leaderboard(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    from sqlalchemy import func
    # Get total footprint per user
    user_totals = db.query(
        models.User.username,
        func.sum(models.Receipt.total_footprint).label('score')
    ).join(models.Receipt).group_by(models.User.id).order_by(func.sum(models.Receipt.total_footprint).desc()).all()

    # Add average household (assume 4.5 tons/year = 4500 kg/year)
    avg_household = {"username": "Average Household", "score": 4500.0}

    leaderboard = [{"username": u.username, "score": round(u.score, 2)} for u in user_totals]
    leaderboard.append(avg_household)

    return leaderboard

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(report.router, prefix="/report", tags=["report"])
app.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
app.include_router(leaderboard_router, prefix="/leaderboard", tags=["leaderboard"])
