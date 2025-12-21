import os
import json
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from .ocr import extract_items_from_image
from .parsers import document_parser
from .enhanced_footprint import EnhancedFootprintMatcher
from .footprint import load_dataset, calculate_offset_from_trees, get_gamification_badge, calculate_trees_needed, calculate_eco_credits, get_credits_needed_for_tree, WhatIfSimulator
from .utils import normalize_quantity
from datetime import datetime, timedelta
from . import auth, report
from . import models, schemas, database
from .carbon_budgeting import (
    CarbonAnalyticsEngine,
    CarbonForecastingEngine,
    AdaptiveCarbonCoach,
    LifestyleSimulator,
    SustainabilityPlanGenerator
)

from fastapi import APIRouter

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title='EcoBasket API')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'], allow_credentials=True)

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Dashboard endpoints (both with and without trailing slash)
@app.get("/dashboard", response_model=list[schemas.DashboardEntry])
@app.get("/dashboard/", response_model=list[schemas.DashboardEntry])
def get_dashboard(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    try:
        from sqlalchemy import func
        # Get monthly totals for the current user (SQLite compatible)
        # SQLite doesn't have to_char, so we use strftime instead
        monthly_data = db.query(
            func.strftime('%Y-%m', models.Receipt.date).label('month'),
            func.sum(models.Receipt.total_footprint).label('total')
        ).filter(models.Receipt.user_id == current_user.id).group_by(func.strftime('%Y-%m', models.Receipt.date)).all()

        return [{"month": m.month, "total": round(m.total, 2)} for m in monthly_data]
    except Exception as e:
        print(f"Dashboard error: {e}")
        import traceback
        traceback.print_exc()
        # Return empty list instead of crashing
        return []

matcher = EnhancedFootprintMatcher(load_dataset(database.DATASET_PATH))
simulator = WhatIfSimulator(load_dataset(database.DATASET_PATH))

# Initialize carbon budgeting engines
analytics_engine = CarbonAnalyticsEngine()
forecasting_engine = CarbonForecastingEngine()
carbon_coach = AdaptiveCarbonCoach()
plan_generator = SustainabilityPlanGenerator()


@app.post('/upload_receipt', response_model=schemas.ReceiptBase)
async def upload_receipt(file: UploadFile = File(...), current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    contents = await file.read()

    try:
        # Use the new document parser system
        parsed_data = document_parser.parse_document(contents)
        items_raw = parsed_data['items']
        document_type = parsed_data['document_type']

    except Exception as e:
        raise HTTPException(status_code=500, detail=f'OCR failed: {e}')

    # Normalize quantities
    items = []
    for it in items_raw:
        qty_kg, _ = normalize_quantity(f"{it.get('qty', 1)} {it.get('name', '')}")
        category = it.get('category', 'food')  # Default to food for backward compatibility
        items.append({
            'name': it.get('name', ''),
            'qty': qty_kg,
            'category': category,
            'unit': it.get('unit', 'kg')
        })

    results, total = matcher.match_and_compute(items)

    # Create receipt and items in DB linked to current user
    receipt = models.Receipt(
        user_id=current_user.id,
        total_footprint=total,
        document_type=document_type,
        date=datetime.utcnow()
    )
    db.add(receipt)
    db.commit()
    db.refresh(receipt)

    # Reset the items sequence to avoid primary key conflicts
    try:
        max_id = db.query(func.max(models.Item.id)).scalar()
        if max_id:
            db.execute(text(f"SELECT setval('items_id_seq', {max_id})"))
            db.commit()
    except Exception as seq_error:
        print(f"Warning: Could not reset sequence: {seq_error}")

    for item in results:
        db_item = models.Item(
            receipt_id=receipt.id,
            name=item['name'],
            matched_name=item['matched_name'],
            qty=item['qty'],
            unit=item['unit'],
            footprint=item['footprint'],
            category=item.get('category', 'food'),
            match_score=item.get('match_score'),
            co2_per_unit=item.get('co2_per_unit')
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
    doc_type_value = receipt.document_type if isinstance(receipt.document_type, str) else receipt.document_type.value
    receipt_data = schemas.ReceiptBase(
        id=receipt.id,
        user_id=receipt.user_id,
        total_footprint=receipt.total_footprint,
        document_type=schemas.DocumentType(doc_type_value),
        items=[schemas.ItemBase(
            name=i.name,
            matched_name=i.matched_name or "",
            qty=i.qty,
            unit=i.unit or "",
            footprint=i.footprint,
            category=getattr(i, 'category', 'food'),
            match_score=getattr(i, 'match_score', None),
            co2_per_unit=getattr(i, 'co2_per_unit', None)
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
            document_type=schemas.DocumentType(receipt.document_type) if isinstance(receipt.document_type, str) else schemas.DocumentType(receipt.document_type.value),
            items=[schemas.ItemBase(
                name=i.name,
                matched_name=i.matched_name or "",
                qty=i.qty,
                unit=i.unit or "",
                footprint=i.footprint,
                category=getattr(i, 'category', 'food'),
                match_score=getattr(i, 'match_score', None),
                co2_per_unit=getattr(i, 'co2_per_unit', None)
            ) for i in items],
            date=receipt.date
        )
        result.append(receipt_data)
    return result

@app.post('/simulate_meat_replacement')
def simulate_meat_replacement(request: schemas.MeatReplacementRequest):
    """
    Simulate replacing meat meals with plant-based alternatives.
    """
    try:
        result = simulator.simulate_meat_replacement(request.meat_meals_per_week, request.weeks)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post('/simulate_transport_switch')
def simulate_transport_switch(request: schemas.TransportSwitchRequest):
    """
    Simulate switching from one transport mode to another.
    """
    try:
        result = simulator.simulate_transport_switch(
            request.trips_per_year,
            request.distance_per_trip_km,
            request.from_mode,
            request.to_mode
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post('/simulate_energy_efficiency')
def simulate_energy_efficiency(request: schemas.EnergyEfficiencyRequest):
    """
    Simulate switching from incandescent to LED bulbs.
    """
    try:
        result = simulator.simulate_energy_efficiency(
            request.current_bulbs,
            request.led_bulbs,
            request.hours_per_day,
            request.days_per_year
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post('/simulate_electric_vehicle')
def simulate_electric_vehicle(request: schemas.ElectricVehicleRequest):
    """
    Simulate switching from gasoline car to electric vehicle.
    """
    try:
        result = simulator.simulate_electric_vehicle(
            request.annual_km,
            request.current_fuel_efficiency,
            request.ev_efficiency
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post('/simulate_local_food')
def simulate_local_food(request: schemas.LocalFoodRequest):
    """
    Simulate choosing local/seasonal food over imported food.
    """
    try:
        result = simulator.simulate_local_food(
            request.imported_meals_per_week,
            request.local_reduction_percent,
            request.weeks
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post('/simulate_waste_reduction')
def simulate_waste_reduction(request: schemas.WasteReductionRequest):
    """
    Simulate reducing food waste.
    """
    try:
        result = simulator.simulate_waste_reduction(
            request.current_waste_kg_per_week,
            request.reduction_percent,
            request.weeks
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

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


# ============================================================================
# CARBON BUDGETING AI ENDPOINTS
# ============================================================================

@app.get('/api/carbon/insights', response_model=schemas.CarbonInsightsResponse)
def get_carbon_insights(
    period: str = "month",
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    """
    Get carbon footprint insights and analysis.
    
    Query params:
    - period: "day", "week", "month" (default: "month")
    
    Returns:
    - Summary statistics
    - Category breakdown
    - Top 5 emission sources
    - Detected recurring patterns
    """
    # Fetch user receipts
    receipts_db = db.query(models.Receipt).filter(
        models.Receipt.user_id == current_user.id
    ).order_by(models.Receipt.date.desc()).all()
    
    if not receipts_db:
        raise HTTPException(status_code=404, detail="No receipts found. Please upload receipts first.")
    
    # Convert receipts to dict format with items
    receipts = []
    for receipt in receipts_db:
        items = db.query(models.Item).filter(models.Item.receipt_id == receipt.id).all()
        receipts.append({
            "date": receipt.date,
            "total_footprint": receipt.total_footprint,
            "items": [
                {
                    "name": i.name,
                    "matched_name": i.matched_name,
                    "qty": i.qty,
                    "unit": i.unit,
                    "footprint": i.footprint,
                    "category": i.category
                }
                for i in items
            ]
        })
    
    # Aggregate by period
    daily_aggregations = analytics_engine.aggregate_by_period(receipts, period=period)
    
    if not daily_aggregations:
        raise HTTPException(status_code=400, detail="Not enough data for analysis")
    
    # Calculate statistics
    values = [d.total_kg for d in daily_aggregations]
    total_footprint = sum(values)
    avg_daily = sum(values) / len(values) if values else 0
    
    # Analyze categories
    categories = analytics_engine.analyze_categories(receipts)
    
    # Get top sources
    top_sources = analytics_engine.get_top_emission_sources(receipts, top_n=5)
    
    # Detect patterns
    patterns = analytics_engine.detect_recurring_patterns(receipts)
    
    # Build response
    period_label = {"day": "daily", "week": "weekly", "month": "monthly"}.get(period, "daily")
    summary = (
        f"Your {period_label} carbon footprint is {avg_daily:.2f} kg CO2. "
        f"Your top emission source is {categories[0].category if categories else 'unknown'} "
        f"({categories[0].percentage if categories else 0}% of total)."
    )
    
    return schemas.CarbonInsightsResponse(
        summary=summary,
        total_footprint_kg=round(total_footprint, 2),
        period=period,
        average_daily_kg=round(avg_daily, 2),
        category_breakdown=[
            schemas.CategoryAnalysisSchema(
                category=c.category,
                total_kg=c.total_kg,
                percentage=c.percentage,
                item_count=c.item_count,
                avg_per_item=c.avg_per_item
            )
            for c in categories
        ],
        top_5_sources=top_sources,
        recurring_patterns=[
            {
                "item": h.item_name,
                "frequency_days": h.frequency_days,
                "annual_impact_kg": h.total_impact_annual_kg,
                "is_subscription_like": h.is_subscription_like
            }
            for h in patterns
        ]
    )


@app.get('/api/carbon/forecast', response_model=schemas.CarbonForecastResponse)
def get_carbon_forecast(
    days: int = 30,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    """
    Get 30-day carbon emissions forecast.
    
    Query params:
    - days: Number of days to forecast (default: 30, max: 90)
    
    Returns:
    - Daily predictions with confidence intervals
    - Overall trend assessment
    """
    days = min(days, 90)  # Cap at 90 days
    
    # Fetch user receipts from last 30 days
    start_date = datetime.utcnow() - timedelta(days=30)
    receipts_db = db.query(models.Receipt).filter(
        models.Receipt.user_id == current_user.id,
        models.Receipt.date >= start_date
    ).order_by(models.Receipt.date).all()
    
    if not receipts_db:
        raise HTTPException(status_code=404, detail="No receipts found. Please upload receipts first.")
    
    # Convert to dict format
    receipts = [
        {
            "date": r.date,
            "total_footprint": r.total_footprint,
            "items": []
        }
        for r in receipts_db
    ]
    
    # Aggregate daily
    daily_aggregations = analytics_engine.aggregate_by_period(receipts, period="day")
    
    # Generate forecast
    forecasts = forecasting_engine.predict_future_emissions(
        daily_aggregations,
        days_ahead=days,
        method="trend"
    )
    
    # Assess risk level
    if forecasts:
        recent_avg = sum([f.predicted_kg for f in forecasts[-7:]]) / 7
        historical_avg = sum([d.total_kg for d in daily_aggregations]) / len(daily_aggregations)
        
        if recent_avg > historical_avg * 1.15:
            risk_level = "high"
        elif recent_avg > historical_avg * 1.05:
            risk_level = "medium"
        else:
            risk_level = "low"
    else:
        risk_level = "unknown"
    
    summary = f"Your emissions are projected to be {risk_level} over the next {days} days."
    
    return schemas.CarbonForecastResponse(
        forecast_days=days,
        forecasts=[
            schemas.ForecastDataSchema(
                date=f.date,
                predicted_kg=f.predicted_kg,
                confidence_interval=f.confidence_interval,
                trend=f.trend
            )
            for f in forecasts
        ],
        summary=summary,
        risk_level=risk_level
    )


@app.post('/api/carbon/simulate', response_model=schemas.SimulationResultSchema)
def simulate_lifestyle_change(
    request: schemas.SimulationChangeRequest,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    """
    Simulate the carbon impact of a lifestyle change.
    
    Request body:
    {
        "change_type": "diet|commute|shopping|energy",
        "parameters": {
            // Type-specific parameters
        }
    }
    
    Examples:
    - Diet: {"change_type": "diet", "parameters": {"reduction_percent": 50}}
    - Commute: {"change_type": "commute", "parameters": {"from_mode": "car", "to_mode": "bike", "days_per_week": 5}}
    - Shopping: {"change_type": "shopping", "parameters": {"reduction_percent": 30}}
    - Energy: {"change_type": "energy", "parameters": {"efficiency_improvement_percent": 20}}
    """
    # Calculate user's current daily average
    receipts_db = db.query(models.Receipt).filter(
        models.Receipt.user_id == current_user.id
    ).all()
    
    if not receipts_db:
        raise HTTPException(status_code=404, detail="No receipts found.")
    
    total = sum([r.total_footprint for r in receipts_db])
    daily_avg = total / len(receipts_db) if receipts_db else 5.0  # Default to 5kg if no data
    
    # Initialize simulator with user's baseline
    lifestyle_sim = LifestyleSimulator(daily_avg)
    
    # Execute simulation based on change type
    try:
        result = lifestyle_sim.simulate_change(
            request.change_type,
            **request.parameters
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return schemas.SimulationResultSchema(
        change_description=result.change_description,
        estimated_reduction_kg=result.estimated_reduction_kg,
        estimated_reduction_percent=result.estimated_reduction_percent,
        annual_impact_kg=result.annual_impact_kg,
        affected_categories=result.affected_categories
    )


@app.get('/api/carbon/coach', response_model=schemas.WeeklyCarbonBudgetSchema)
def get_carbon_coach(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    """
    Get adaptive weekly carbon budget and recommendations.
    
    Returns:
    - Recommended weekly and daily carbon limits
    - Practical tradeoff suggestions
    - Progress tracking
    """
    # Fetch recent receipts
    start_date = datetime.utcnow() - timedelta(days=30)
    receipts_db = db.query(models.Receipt).filter(
        models.Receipt.user_id == current_user.id,
        models.Receipt.date >= start_date
    ).order_by(models.Receipt.date).all()
    
    if not receipts_db:
        raise HTTPException(status_code=404, detail="No receipts found.")
    
    # Convert to dict format
    receipts = [
        {
            "date": r.date,
            "total_footprint": r.total_footprint,
            "items": []
        }
        for r in receipts_db
    ]
    
    # Aggregate daily
    daily_aggregations = analytics_engine.aggregate_by_period(receipts, period="day")
    
    # Get budget recommendation
    budget = carbon_coach.calculate_weekly_budget(daily_aggregations)
    
    # Calculate current week's progress
    week_start = datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())
    week_receipts = db.query(models.Receipt).filter(
        models.Receipt.user_id == current_user.id,
        models.Receipt.date >= week_start
    ).all()
    
    week_total = sum([r.total_footprint for r in week_receipts])
    progress_percent = (week_total / budget.recommended_weekly_limit_kg) * 100 if budget.recommended_weekly_limit_kg > 0 else 0
    
    return schemas.WeeklyCarbonBudgetSchema(
        week_start_date=budget.week_start_date,
        week_end_date=budget.week_end_date,
        recommended_weekly_limit_kg=budget.recommended_weekly_limit_kg,
        recommended_daily_limit_kg=budget.recommended_daily_limit_kg,
        historical_weekly_avg=budget.historical_weekly_avg,
        progress_percent=round(min(progress_percent, 100), 1),
        tradeoff_suggestions=budget.tradeoff_suggestions
    )


@app.get('/api/carbon/plan/30-day', response_model=schemas.ThirtyDayPlanSchema)
def get_30day_plan(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    """
    Generate comprehensive 30-day personalized sustainability plan.
    
    Returns:
    - Current footprint analysis
    - 3 biggest problem areas
    - 30 days of actionable steps
    - Low-carbon recipe recommendations
    - Commute optimization ideas
    - Subscription/habit changes
    """
    # Fetch all user receipts
    receipts_db = db.query(models.Receipt).filter(
        models.Receipt.user_id == current_user.id
    ).order_by(models.Receipt.date.desc()).all()
    
    if not receipts_db:
        raise HTTPException(status_code=404, detail="No receipts found.")
    
    # Convert to dict format
    receipts = []
    for receipt in receipts_db:
        items = db.query(models.Item).filter(models.Item.receipt_id == receipt.id).all()
        receipts.append({
            "date": receipt.date,
            "total_footprint": receipt.total_footprint,
            "items": [
                {
                    "name": i.name,
                    "matched_name": i.matched_name,
                    "qty": i.qty,
                    "unit": i.unit,
                    "footprint": i.footprint,
                    "category": i.category
                }
                for i in items
            ]
        })
    
    # Analyze data
    daily_aggregations = analytics_engine.aggregate_by_period(receipts, period="day")
    categories = analytics_engine.analyze_categories(receipts)
    habits = analytics_engine.detect_recurring_patterns(receipts)
    
    # Calculate daily average for forecasting
    user_daily_avg = sum([d.total_kg for d in daily_aggregations]) / len(daily_aggregations) if daily_aggregations else 5.0
    
    # Generate forecast
    forecasts = forecasting_engine.predict_future_emissions(daily_aggregations, days_ahead=30)
    
    # Generate plan
    plan = plan_generator.generate_30_day_plan(user_daily_avg, categories, habits, forecasts)
    
    # Save plan to database
    db_plan = models.SustainabilityPlan(
        user_id=current_user.id,
        start_date=datetime.fromisoformat(plan.start_date),
        end_date=datetime.fromisoformat(plan.end_date),
        current_weekly_avg_kg=plan.current_weekly_avg_kg,
        target_weekly_avg_kg=plan.target_weekly_avg_kg,
        total_potential_savings_kg=plan.total_potential_savings_kg,
        summary=plan.summary
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    
    # Save daily actions
    for day_plan in plan.daily_plan:
        db_action = models.DailyPlanAction(
            plan_id=db_plan.id,
            day=day_plan.day,
            focus_area=day_plan.focus_area,
            action=day_plan.action,
            carbon_saved_kg=day_plan.carbon_saved_vs_typical_kg,
            difficulty_level=day_plan.difficulty_level
        )
        db.add(db_action)
    db.commit()
    
    # Return response
    return schemas.ThirtyDayPlanSchema(
        start_date=plan.start_date,
        end_date=plan.end_date,
        current_weekly_avg_kg=plan.current_weekly_avg_kg,
        target_weekly_avg_kg=plan.target_weekly_avg_kg,
        total_potential_savings_kg=plan.total_potential_savings_kg,
        summary=plan.summary,
        problem_areas=[
            schemas.CategoryAnalysisSchema(
                category=p.category,
                total_kg=p.total_kg,
                percentage=p.percentage,
                item_count=p.item_count,
                avg_per_item=p.avg_per_item
            )
            for p in plan.problem_areas
        ],
        improvement_checklist=plan.improvement_checklist,
        recipes=[
            schemas.RecipeSuggestionSchema(
                name=r.name,
                carbon_footprint_kg=r.carbon_footprint_kg,
                protein_g=r.protein_g,
                prep_time_minutes=r.prep_time_minutes,
                ingredients=r.ingredients,
                savings_vs_typical_kg=r.savings_vs_typical_kg
            )
            for r in plan.recipes
        ],
        commute_alternatives=[
            schemas.CommuteOptionSchema(
                mode=c.mode,
                annual_carbon_kg=c.annual_carbon_kg,
                cost_per_month=c.cost_per_month,
                time_per_day_minutes=c.time_per_day_minutes,
                feasibility_score=c.feasibility_score
            )
            for c in plan.commute_alternatives
        ],
        habit_changes=plan.habit_changes,
        subscriptions_to_replace=[
            schemas.SubscriptionToReplaceSchema(
                item_name=s.item_name,
                frequency=s.frequency,
                annual_carbon_kg=s.annual_carbon_kg,
                alternative=s.alternative,
                potential_savings_kg=s.potential_savings_kg
            )
            for s in plan.subscriptions_to_replace
        ],
        daily_plan=[
            schemas.DailyPlanActionSchema(
                day=d.day,
                focus_area=d.focus_area,
                action=d.action,
                carbon_saved_vs_typical_kg=d.carbon_saved_vs_typical_kg,
                difficulty_level=d.difficulty_level
            )
            for d in plan.daily_plan
        ]
    )


app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(report.router, prefix="/report", tags=["report"])
app.include_router(leaderboard_router, prefix="/leaderboard", tags=["leaderboard"])
