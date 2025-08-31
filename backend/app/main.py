import os
import json
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .ocr import extract_items_from_image
from .footprint import FootprintMatcher, load_dataset
from .utils import normalize_quantity
from datetime import datetime
from . import auth, report
from . import models, schemas, database

from fastapi import APIRouter

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title='EcoBasket API')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

matcher = FootprintMatcher(load_dataset(database.DATASET_PATH))

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

    receipt_items = db.query(models.Item).filter(models.Item.receipt_id == receipt.id).all()
    receipt_data = schemas.ReceiptBase(
        id=receipt.id,
        user_id=receipt.user_id,
        total_footprint=receipt.total_footprint,
        items=[schemas.ItemBase(
            name=i.name,
            matched_name=i.matched_name,
            qty=i.qty,
            unit=i.unit,
            footprint=i.footprint
        ) for i in receipt_items]
    )
    return receipt_data

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
                matched_name=i.matched_name,
                qty=i.qty,
                unit=i.unit,
                footprint=i.footprint
            ) for i in items]
        )
        result.append(receipt_data)
    return result

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
