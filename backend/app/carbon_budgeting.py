"""
Carbon Budgeting AI + Sustainability Planner Module

This module provides:
- Carbon footprint analysis and aggregation
- Time-series forecasting of emissions
- Adaptive carbon budgeting recommendations
- Lifestyle simulation and what-if analysis
- 30-day personalized sustainability plans
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import statistics
import math


# ============================================================================
# DATA CLASSES FOR TYPE SAFETY
# ============================================================================

@dataclass
class DailyFootprint:
    """Daily carbon footprint aggregation"""
    date: str
    total_kg: float
    category_breakdown: Dict[str, float]
    item_count: int


@dataclass
class CategoryAnalysis:
    """Analysis of a specific category's emissions"""
    category: str
    total_kg: float
    percentage: float
    item_count: int
    avg_per_item: float


@dataclass
class ForecastData:
    """Time-series forecast data point"""
    date: str
    predicted_kg: float
    confidence_interval: Tuple[float, float]
    trend: str  # "increasing", "stable", "decreasing"


@dataclass
class SimulationResult:
    """Result of a lifestyle change simulation"""
    change_description: str
    estimated_reduction_kg: float
    estimated_reduction_percent: float
    annual_impact_kg: float
    affected_categories: List[str]


@dataclass
class WeeklyCarbonBudget:
    """Weekly carbon budget recommendation"""
    week_start_date: str
    week_end_date: str
    recommended_weekly_limit_kg: float
    recommended_daily_limit_kg: float
    historical_weekly_avg: float
    tradeoff_suggestions: List[str]


@dataclass
class HabitPattern:
    """Detected recurring purchase habit"""
    category: str
    item_name: str
    frequency_days: int
    avg_carbon_per_purchase_kg: float
    total_impact_annual_kg: float
    is_subscription_like: bool


@dataclass
class RecipeSuggestion:
    """Low-carbon recipe recommendation"""
    name: str
    carbon_footprint_kg: float
    protein_g: float
    prep_time_minutes: int
    ingredients: List[str]
    savings_vs_typical_kg: float


@dataclass
class CommuteOption:
    """Commute alternative option"""
    mode: str
    annual_carbon_kg: float
    cost_per_month: float
    time_per_day_minutes: int
    feasibility_score: float  # 0-10


@dataclass
class SubscriptionToReplace:
    """Subscription or recurring purchase to replace"""
    item_name: str
    frequency: str
    annual_carbon_kg: float
    alternative: str
    potential_savings_kg: float


@dataclass
class SustainabilityPlanDay:
    """Single day's plan within 30-day plan"""
    day: int
    focus_area: str
    action: str
    carbon_saved_vs_typical_kg: Optional[float]
    difficulty_level: str  # "easy", "medium", "hard"


@dataclass
class ThirtyDayPlan:
    """Complete 30-day personalized sustainability plan"""
    start_date: str
    end_date: str
    current_weekly_avg_kg: float
    target_weekly_avg_kg: float
    total_potential_savings_kg: float
    summary: str
    problem_areas: List[CategoryAnalysis]
    improvement_checklist: List[str]
    recipes: List[RecipeSuggestion]
    commute_alternatives: List[CommuteOption]
    habit_changes: List[str]
    subscriptions_to_replace: List[SubscriptionToReplace]
    daily_plan: List[SustainabilityPlanDay]


# ============================================================================
# CARBON ANALYTICS ENGINE
# ============================================================================

class CarbonAnalyticsEngine:
    """Main engine for carbon footprint analysis and insights"""
    
    def __init__(self):
        """Initialize the analytics engine"""
        self.min_data_points = 3  # Minimum receipts for analysis
    
    def aggregate_by_period(
        self,
        receipts: List[Dict],
        period: str = "day"  # "day", "week", "month"
    ) -> List[DailyFootprint]:
        """
        Aggregate emissions by specified period.
        
        Args:
            receipts: List of receipt dicts with 'date', 'total_footprint', 'items'
            period: Aggregation period
        
        Returns:
            List of aggregated footprints
        """
        if not receipts:
            return []
        
        aggregated = defaultdict(lambda: {"total": 0.0, "categories": defaultdict(float), "count": 0})
        
        for receipt in receipts:
            date = receipt["date"]
            
            # Parse date to determine period key
            if isinstance(date, str):
                date_obj = datetime.fromisoformat(date.replace("Z", "+00:00"))
            else:
                date_obj = date
            
            # Calculate period key
            if period == "day":
                period_key = date_obj.date().isoformat()
            elif period == "week":
                # ISO week start (Monday)
                week_start = date_obj - timedelta(days=date_obj.weekday())
                period_key = f"week_{week_start.date().isoformat()}"
            elif period == "month":
                period_key = date_obj.strftime("%Y-%m")
            else:
                period_key = date_obj.date().isoformat()
            
            # Accumulate data
            footprint = receipt.get("total_footprint", 0)
            aggregated[period_key]["total"] += footprint
            aggregated[period_key]["count"] += 1
            
            # Category breakdown
            items = receipt.get("items", [])
            for item in items:
                category = item.get("category", "other")
                item_footprint = item.get("footprint", 0)
                aggregated[period_key]["categories"][category] += item_footprint
        
        # Convert to DailyFootprint objects
        result = []
        for period_key in sorted(aggregated.keys()):
            data = aggregated[period_key]
            result.append(DailyFootprint(
                date=period_key,
                total_kg=round(data["total"], 2),
                category_breakdown=dict(data["categories"]),
                item_count=data["count"]
            ))
        
        return result
    
    def analyze_categories(
        self,
        receipts: List[Dict]
    ) -> List[CategoryAnalysis]:
        """
        Analyze emissions breakdown by category.
        
        Returns:
            Sorted list of categories by carbon impact
        """
        if not receipts:
            return []
        
        category_data = defaultdict(lambda: {"total": 0.0, "count": 0})
        total_footprint = 0.0
        
        for receipt in receipts:
            items = receipt.get("items", [])
            for item in items:
                category = item.get("category", "other")
                footprint = item.get("footprint", 0)
                category_data[category]["total"] += footprint
                category_data[category]["count"] += 1
                total_footprint += footprint
        
        if total_footprint == 0:
            return []
        
        # Create analysis objects
        analyses = []
        for category, data in category_data.items():
            analyses.append(CategoryAnalysis(
                category=category,
                total_kg=round(data["total"], 2),
                percentage=round((data["total"] / total_footprint) * 100, 1),
                item_count=data["count"],
                avg_per_item=round(data["total"] / data["count"], 2) if data["count"] > 0 else 0
            ))
        
        # Sort by total impact descending
        analyses.sort(key=lambda x: x.total_kg, reverse=True)
        return analyses
    
    def get_top_emission_sources(
        self,
        receipts: List[Dict],
        top_n: int = 5
    ) -> List[Dict]:
        """
        Identify top N emission sources (specific items).
        
        Returns:
            List of top items by carbon impact
        """
        item_totals = defaultdict(float)
        item_counts = defaultdict(int)
        
        for receipt in receipts:
            items = receipt.get("items", [])
            for item in items:
                name = item.get("matched_name", item.get("name", "unknown"))
                footprint = item.get("footprint", 0)
                item_totals[name] += footprint
                item_counts[name] += 1
        
        # Create list of (name, total, frequency)
        sources = [
            {
                "item": name,
                "total_kg": round(total, 2),
                "frequency": item_counts[name],
                "avg_per_purchase_kg": round(total / item_counts[name], 2)
            }
            for name, total in item_totals.items()
        ]
        
        # Sort by total impact
        sources.sort(key=lambda x: x["total_kg"], reverse=True)
        return sources[:top_n]
    
    def detect_recurring_patterns(
        self,
        receipts: List[Dict]
    ) -> List[HabitPattern]:
        """
        Detect recurring purchase patterns (like subscriptions).
        
        Returns:
            List of detected habits
        """
        # Track item occurrences with dates
        item_dates = defaultdict(list)
        item_totals = defaultdict(float)
        
        for receipt in receipts:
            date = receipt["date"]
            if isinstance(date, str):
                date_obj = datetime.fromisoformat(date.replace("Z", "+00:00"))
            else:
                date_obj = date
            
            items = receipt.get("items", [])
            for item in items:
                name = item.get("matched_name", item.get("name", "unknown"))
                category = item.get("category", "other")
                footprint = item.get("footprint", 0)
                
                item_dates[name].append({
                    "date": date_obj,
                    "category": category,
                    "footprint": footprint
                })
                item_totals[name] += footprint
        
        patterns = []
        
        # Analyze frequency patterns
        for name, occurrences in item_dates.items():
            if len(occurrences) < 2:
                continue  # Need at least 2 occurrences
            
            # Sort by date
            occurrences_sorted = sorted(occurrences, key=lambda x: x["date"])
            
            # Calculate intervals between purchases
            intervals = []
            for i in range(len(occurrences_sorted) - 1):
                delta = (occurrences_sorted[i + 1]["date"] - occurrences_sorted[i]["date"]).days
                if delta > 0:
                    intervals.append(delta)
            
            if not intervals:
                continue
            
            # Average interval
            avg_interval = statistics.mean(intervals)
            variance = statistics.stdev(intervals) if len(intervals) > 1 else 0
            
            # Check if recurring (low variance = regular pattern)
            is_subscription_like = variance < avg_interval * 0.5  # Coefficient of variation < 50%
            
            if is_subscription_like or avg_interval < 30:  # Weekly-ish or more frequent
                category = occurrences[0]["category"]
                avg_carbon = item_totals[name] / len(occurrences)
                
                patterns.append(HabitPattern(
                    category=category,
                    item_name=name,
                    frequency_days=round(avg_interval),
                    avg_carbon_per_purchase_kg=round(avg_carbon, 2),
                    total_impact_annual_kg=round(avg_carbon * (365 / avg_interval), 2),
                    is_subscription_like=is_subscription_like
                ))
        
        # Sort by annual impact
        patterns.sort(key=lambda x: x.total_impact_annual_kg, reverse=True)
        return patterns


# ============================================================================
# CARBON FORECASTING ENGINE
# ============================================================================

class CarbonForecastingEngine:
    """Time-series forecasting and prediction engine"""
    
    def __init__(self):
        """Initialize forecasting engine"""
        self.min_days = 7  # Minimum historical data for forecast
    
    def predict_future_emissions(
        self,
        daily_footprints: List[DailyFootprint],
        days_ahead: int = 30,
        method: str = "trend"  # "trend", "seasonal", "hybrid"
    ) -> List[ForecastData]:
        """
        Predict future emissions using time-series heuristics.
        
        Args:
            daily_footprints: Historical daily aggregations
            days_ahead: Number of days to forecast
            method: Forecasting method
        
        Returns:
            List of forecasted daily values
        """
        if len(daily_footprints) < self.min_days:
            # Not enough data; return simple constant forecast
            if daily_footprints:
                avg = statistics.mean([d.total_kg for d in daily_footprints])
            else:
                avg = 0
            
            start_date = datetime.now().date()
            return [
                ForecastData(
                    date=(start_date + timedelta(days=i)).isoformat(),
                    predicted_kg=round(avg, 2),
                    confidence_interval=(round(avg * 0.8, 2), round(avg * 1.2, 2)),
                    trend="stable"
                )
                for i in range(days_ahead)
            ]
        
        # Extract values
        values = [d.total_kg for d in daily_footprints]
        
        # Simple trend calculation
        if len(values) >= 2:
            recent_avg = statistics.mean(values[-7:]) if len(values) >= 7 else statistics.mean(values)
            older_avg = statistics.mean(values[:-7]) if len(values) >= 7 else statistics.mean(values[:max(1, len(values)-7)])
            
            trend_slope = (recent_avg - older_avg) / 7 if len(values) >= 7 else 0
        else:
            trend_slope = 0
        
        overall_avg = statistics.mean(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else overall_avg * 0.1
        
        # Generate forecast
        forecast = []
        start_date = datetime.now().date()
        
        for i in range(days_ahead):
            # Linear trend extrapolation
            predicted = overall_avg + (trend_slope * i / 7)
            predicted = max(0, predicted)  # No negative emissions
            
            # Confidence interval (widens with forecast distance)
            confidence = std_dev * (1 + i / days_ahead)
            lower = max(0, predicted - confidence)
            upper = predicted + confidence
            
            # Determine trend direction
            if trend_slope > std_dev * 0.1:
                trend = "increasing"
            elif trend_slope < -std_dev * 0.1:
                trend = "decreasing"
            else:
                trend = "stable"
            
            forecast.append(ForecastData(
                date=(start_date + timedelta(days=i)).isoformat(),
                predicted_kg=round(predicted, 2),
                confidence_interval=(round(lower, 2), round(upper, 2)),
                trend=trend
            ))
        
        return forecast
    
    def predict_with_lifestyle_change(
        self,
        current_avg_daily_kg: float,
        affected_categories: Dict[str, float],
        change_percent: float
    ) -> float:
        """
        Predict daily emissions after a lifestyle change.
        
        Args:
            current_avg_daily_kg: Current average daily footprint
            affected_categories: Dict of {category: percentage_of_daily}
            change_percent: Change percentage (e.g., -20 for 20% reduction)
        
        Returns:
            Predicted new daily footprint
        """
        reduction = 0.0
        for category, pct in affected_categories.items():
            category_impact = current_avg_daily_kg * (pct / 100)
            reduction += category_impact * (abs(change_percent) / 100)
        
        return max(0, current_avg_daily_kg - reduction)


# ============================================================================
# ADAPTIVE CARBON COACH
# ============================================================================

class AdaptiveCarbonCoach:
    """Generates adaptive carbon budgets and recommendations"""
    
    def __init__(self):
        """Initialize coach"""
        self.target_reduction_percent = 15  # Target 15% reduction over 30 days
    
    def calculate_weekly_budget(
        self,
        daily_footprints: List[DailyFootprint],
        target_percent_reduction: Optional[float] = None
    ) -> WeeklyCarbonBudget:
        """
        Calculate weekly carbon budget with reduction targets.
        
        Args:
            daily_footprints: Historical daily data
            target_percent_reduction: Target reduction % (default: 15%)
        
        Returns:
            Weekly budget recommendation
        """
        if not daily_footprints:
            # No data; use conservative default
            default_daily = 5.0  # kg CO2
            return WeeklyCarbonBudget(
                week_start_date=datetime.now().date().isoformat(),
                week_end_date=(datetime.now().date() + timedelta(days=6)).isoformat(),
                recommended_weekly_limit_kg=round(default_daily * 7, 2),
                recommended_daily_limit_kg=round(default_daily, 2),
                historical_weekly_avg=0,
                tradeoff_suggestions=[]
            )
        
        if target_percent_reduction is None:
            target_percent_reduction = self.target_reduction_percent
        
        # Calculate historical weekly average
        historical_avg_daily = statistics.mean([d.total_kg for d in daily_footprints])
        historical_weekly = round(historical_avg_daily * 7, 2)
        
        # Apply target reduction
        target_daily = historical_avg_daily * (1 - target_percent_reduction / 100)
        target_weekly = round(target_daily * 7, 2)
        
        # Generate tradeoff suggestions
        tradeoffs = self._generate_tradeoffs(daily_footprints, historical_avg_daily)
        
        week_start = datetime.now().date()
        week_end = week_start + timedelta(days=6)
        
        return WeeklyCarbonBudget(
            week_start_date=week_start.isoformat(),
            week_end_date=week_end.isoformat(),
            recommended_weekly_limit_kg=target_weekly,
            recommended_daily_limit_kg=round(target_daily, 2),
            historical_weekly_avg=historical_weekly,
            tradeoff_suggestions=tradeoffs
        )
    
    def _generate_tradeoffs(
        self,
        daily_footprints: List[DailyFootprint],
        avg_daily: float
    ) -> List[str]:
        """Generate practical tradeoff suggestions"""
        tradeoffs = [
            "If you buy beef twice this week, skip the takeout meals to stay under budget.",
            "Choosing plant-based proteins for 3 meals saves ~1.5 kg CO2 this week.",
            "Buying local vegetables instead of imported ones saves ~0.8 kg CO2.",
            "One less car trip per day saves ~2 kg CO2 weekly.",
            "Choosing products with minimal packaging saves ~0.5 kg CO2.",
            "One meatless day saves ~1.2 kg CO2 from your weekly budget.",
            "Buying in bulk reduces emissions from packaging by ~10%.",
            "Seasonal produce has 30% lower carbon footprint than out-of-season."
        ]
        
        # Return top 3 relevant suggestions
        import random
        random.seed(int(avg_daily * 100))  # Deterministic but varied
        selected = random.sample(tradeoffs, min(3, len(tradeoffs)))
        return selected


# ============================================================================
# LIFESTYLE SIMULATION ENGINE
# ============================================================================

class LifestyleSimulator:
    """Simulates carbon impact of lifestyle changes"""
    
    def __init__(self, historical_daily_avg: float):
        """
        Initialize simulator.
        
        Args:
            historical_daily_avg: User's average daily carbon footprint
        """
        self.daily_avg = historical_daily_avg
    
    def simulate_change(
        self,
        change_type: str,
        **kwargs
    ) -> SimulationResult:
        """
        Simulate a specific lifestyle change.
        
        Args:
            change_type: Type of change ("diet", "commute", "shopping", etc.)
            **kwargs: Type-specific parameters
        
        Returns:
            Simulation result with impact estimates
        """
        if change_type == "diet":
            return self._simulate_diet_change(**kwargs)
        elif change_type == "commute":
            return self._simulate_commute_change(**kwargs)
        elif change_type == "shopping":
            return self._simulate_shopping_change(**kwargs)
        elif change_type == "energy":
            return self._simulate_energy_change(**kwargs)
        else:
            raise ValueError(f"Unknown change type: {change_type}")
    
    def _simulate_diet_change(
        self,
        reduction_percent: int,
        removed_items: Optional[List[str]] = None
    ) -> SimulationResult:
        """Simulate dietary changes"""
        # Food typically accounts for 25-35% of personal carbon footprint
        food_percent = 30
        daily_food_impact = self.daily_avg * (food_percent / 100)
        
        reduction = daily_food_impact * (reduction_percent / 100)
        
        return SimulationResult(
            change_description=f"Reducing meat consumption by {reduction_percent}%",
            estimated_reduction_kg=round(reduction, 2),
            estimated_reduction_percent=round((reduction / self.daily_avg) * 100, 1),
            annual_impact_kg=round(reduction * 365, 2),
            affected_categories=["food"]
        )
    
    def _simulate_commute_change(
        self,
        from_mode: str,
        to_mode: str,
        days_per_week: int = 5
    ) -> SimulationResult:
        """Simulate commute change"""
        # Typical daily commute emissions (kg CO2)
        commute_emissions = {
            "car": 8.0,      # Solo car commute
            "bike": 0.0,     # Zero emissions
            "public_transit": 1.5,
            "walk": 0.0,
            "carpool": 2.0
        }
        
        from_daily = commute_emissions.get(from_mode, 5.0)
        to_daily = commute_emissions.get(to_mode, 5.0)
        
        weekly_reduction = (from_daily - to_daily) * days_per_week
        daily_reduction = weekly_reduction / 7
        
        return SimulationResult(
            change_description=f"Switching commute from {from_mode} to {to_mode}",
            estimated_reduction_kg=round(daily_reduction, 2),
            estimated_reduction_percent=round((daily_reduction / self.daily_avg) * 100, 1),
            annual_impact_kg=round(daily_reduction * 365, 2),
            affected_categories=["transport"]
        )
    
    def _simulate_shopping_change(
        self,
        reduction_percent: int,
        focused_categories: Optional[List[str]] = None
    ) -> SimulationResult:
        """Simulate shopping habit changes"""
        # Consumer goods account for ~30% of footprint
        shopping_percent = 30
        daily_shopping_impact = self.daily_avg * (shopping_percent / 100)
        
        reduction = daily_shopping_impact * (reduction_percent / 100)
        
        categories = focused_categories or ["clothing", "goods", "electronics"]
        
        return SimulationResult(
            change_description=f"Reducing new purchases by {reduction_percent}% (secondhand/sustainable)",
            estimated_reduction_kg=round(reduction, 2),
            estimated_reduction_percent=round((reduction / self.daily_avg) * 100, 1),
            annual_impact_kg=round(reduction * 365, 2),
            affected_categories=categories
        )
    
    def _simulate_energy_change(
        self,
        efficiency_improvement_percent: int = 20
    ) -> SimulationResult:
        """Simulate home energy efficiency improvements"""
        # Home energy typically 25-30% of footprint
        energy_percent = 25
        daily_energy_impact = self.daily_avg * (energy_percent / 100)
        
        reduction = daily_energy_impact * (efficiency_improvement_percent / 100)
        
        return SimulationResult(
            change_description=f"Improving energy efficiency by {efficiency_improvement_percent}%",
            estimated_reduction_kg=round(reduction, 2),
            estimated_reduction_percent=round((reduction / self.daily_avg) * 100, 1),
            annual_impact_kg=round(reduction * 365, 2),
            affected_categories=["energy"]
        )


# ============================================================================
# SUSTAINABILITY PLAN GENERATOR
# ============================================================================

class SustainabilityPlanGenerator:
    """Generates personalized 30-day sustainability plans"""
    
    # Low-carbon recipe database
    RECIPES = [
        RecipeSuggestion(
            name="Lentil Buddha Bowl",
            carbon_footprint_kg=0.8,
            protein_g=15,
            prep_time_minutes=20,
            ingredients=["lentils", "quinoa", "roasted vegetables", "tahini dressing"],
            savings_vs_typical_kg=2.1
        ),
        RecipeSuggestion(
            name="Chickpea Curry",
            carbon_footprint_kg=0.9,
            protein_g=14,
            prep_time_minutes=30,
            ingredients=["chickpeas", "coconut milk", "curry spices", "onions", "garlic"],
            savings_vs_typical_kg=2.0
        ),
        RecipeSuggestion(
            name="Tofu Stir-Fry",
            carbon_footprint_kg=0.7,
            protein_g=18,
            prep_time_minutes=25,
            ingredients=["firm tofu", "mixed vegetables", "soy sauce", "garlic"],
            savings_vs_typical_kg=2.2
        ),
        RecipeSuggestion(
            name="Bean & Vegetable Chili",
            carbon_footprint_kg=0.85,
            protein_g=16,
            prep_time_minutes=35,
            ingredients=["black beans", "kidney beans", "tomatoes", "peppers", "chili spices"],
            savings_vs_typical_kg=2.15
        ),
        RecipeSuggestion(
            name="Mediterranean Salad",
            carbon_footprint_kg=0.5,
            protein_g=10,
            prep_time_minutes=15,
            ingredients=["mixed greens", "chickpeas", "tomatoes", "cucumber", "olive oil"],
            savings_vs_typical_kg=1.8
        ),
        RecipeSuggestion(
            name="Whole Grain Pasta Primavera",
            carbon_footprint_kg=0.6,
            protein_g=12,
            prep_time_minutes=20,
            ingredients=["whole grain pasta", "seasonal vegetables", "olive oil", "garlic"],
            savings_vs_typical_kg=1.9
        ),
        RecipeSuggestion(
            name="Vegetable Soup",
            carbon_footprint_kg=0.45,
            protein_g=8,
            prep_time_minutes=30,
            ingredients=["vegetable broth", "seasonal vegetables", "beans", "herbs"],
            savings_vs_typical_kg=1.7
        ),
        RecipeSuggestion(
            name="Mushroom Risotto",
            carbon_footprint_kg=1.1,
            protein_g=9,
            prep_time_minutes=35,
            ingredients=["arborio rice", "mushrooms", "vegetable broth", "parmesan"],
            savings_vs_typical_kg=1.8
        ),
    ]
    
    # Commute alternatives database
    COMMUTE_OPTIONS = [
        CommuteOption(
            mode="Electric Bike",
            annual_carbon_kg=0.02 * 365,
            cost_per_month=50,
            time_per_day_minutes=18,
            feasibility_score=7.5
        ),
        CommuteOption(
            mode="Public Transit",
            annual_carbon_kg=1.5 * 365,
            cost_per_month=80,
            time_per_day_minutes=35,
            feasibility_score=8.0
        ),
        CommuteOption(
            mode="Carpool",
            annual_carbon_kg=2.0 * 365,
            cost_per_month=100,
            time_per_day_minutes=25,
            feasibility_score=6.5
        ),
        CommuteOption(
            mode="Hybrid Work",
            annual_carbon_kg=2.0 * 365,
            cost_per_month=0,
            time_per_day_minutes=0,
            feasibility_score=7.0
        ),
        CommuteOption(
            mode="Walking",
            annual_carbon_kg=0.0,
            cost_per_month=0,
            time_per_day_minutes=25,
            feasibility_score=5.0
        ),
    ]
    
    def generate_30_day_plan(
        self,
        user_daily_avg: float,
        category_analysis: List[CategoryAnalysis],
        habits: List[HabitPattern],
        forecasts: List[ForecastData]
    ) -> ThirtyDayPlan:
        """
        Generate comprehensive 30-day sustainability plan.
        
        Args:
            user_daily_avg: User's average daily footprint
            category_analysis: Analysis of emission categories
            habits: Detected recurring patterns
            forecasts: 30-day forecasts
        
        Returns:
            Complete 30-day plan
        """
        # Filter out None habits
        habits = [h for h in habits if h is not None]
        today = datetime.now().date()
        end_date = today + timedelta(days=29)
        
        # Identify top 3 problem areas
        problem_areas = category_analysis[:3]
        
        # Calculate targets
        target_reduction = 15  # 15% reduction
        current_weekly = user_daily_avg * 7
        target_weekly = current_weekly * (1 - target_reduction / 100)
        total_savings = (current_weekly - target_weekly) * 4  # 4 weeks
        
        # Build improvement checklist
        checklist = self._build_improvement_checklist(problem_areas, habits)
        
        # Select recipes
        recipes = self._select_recipes(4)
        
        # Commute options
        commute_opts = self._recommend_commute_options(2)
        
        # Habit changes
        habit_changes = self._recommend_habit_changes(habits)
        
        # Subscriptions to replace
        subscriptions = self._identify_subscriptions_to_replace(habits)
        
        # Generate daily plan
        daily_plan = self._generate_daily_plan(30, problem_areas)
        
        # Summary
        summary = (
            f"Your current weekly footprint is {current_weekly:.1f} kg CO2. "
            f"Over 30 days, we can reduce this to {target_weekly:.1f} kg/week "
            f"by focusing on {problem_areas[0].category if problem_areas else 'sustainable choices'}. "
            f"Your top 3 improvement opportunities are in {', '.join([p.category for p in problem_areas])}."
        )
        
        return ThirtyDayPlan(
            start_date=today.isoformat(),
            end_date=end_date.isoformat(),
            current_weekly_avg_kg=round(current_weekly, 2),
            target_weekly_avg_kg=round(target_weekly, 2),
            total_potential_savings_kg=round(total_savings, 2),
            summary=summary,
            problem_areas=problem_areas,
            improvement_checklist=checklist,
            recipes=recipes,
            commute_alternatives=commute_opts,
            habit_changes=habit_changes,
            subscriptions_to_replace=subscriptions,
            daily_plan=daily_plan
        )
    
    def _build_improvement_checklist(
        self,
        problem_areas: List[CategoryAnalysis],
        habits: List[HabitPattern]
    ) -> List[str]:
        """Build action checklist"""
        checklist = []
        
        for area in problem_areas:
            if area.category == "food":
                checklist.extend([
                    "✓ Try 2 meatless days this week",
                    "✓ Buy local and seasonal produce",
                    "✓ Reduce single-use food packaging"
                ])
            elif area.category == "transport":
                checklist.extend([
                    "✓ Bike or walk for trips under 2 km",
                    "✓ Carpool or use public transit twice",
                    "✓ Plan routes to combine errands"
                ])
            elif area.category == "shopping" or area.category == "goods":
                checklist.extend([
                    "✓ Buy secondhand clothing",
                    "✓ Repair items instead of replacing",
                    "✓ Unsubscribe from unnecessary deliveries"
                ])
        
        # Add habit-specific items
        for habit in habits[:2]:
            if habit.is_subscription_like:
                checklist.append(f"✓ Review subscription to {habit.item_name}")
        
        return checklist[:7]  # Return top 7
    
    def _select_recipes(self, count: int) -> List[RecipeSuggestion]:
        """Select random recipes"""
        import random
        return random.sample(self.RECIPES, min(count, len(self.RECIPES)))
    
    def _recommend_commute_options(self, count: int) -> List[CommuteOption]:
        """Recommend commute alternatives"""
        # Return top feasible options
        sorted_options = sorted(
            self.COMMUTE_OPTIONS,
            key=lambda x: x.feasibility_score,
            reverse=True
        )
        return sorted_options[:count]
    
    def _recommend_habit_changes(self, habits: List[HabitPattern]) -> List[str]:
        """Generate habit change recommendations"""
        recommendations = []
        
        for habit in habits[:3]:
            if habit.is_subscription_like:
                savings = habit.total_impact_annual_kg
                rec = (
                    f"Replace {habit.item_name} with a lower-carbon alternative "
                    f"(saves ~{savings:.1f} kg CO2/year)"
                )
                recommendations.append(rec)
        
        return recommendations or [
            "Try meatless Mondays",
            "Switch to reusable shopping bags",
            "Buy items in bulk to reduce packaging"
        ]
    
    def _identify_subscriptions_to_replace(
        self,
        habits: List[HabitPattern]
    ) -> List[SubscriptionToReplace]:
        """Identify recurring purchases to replace"""
        subscriptions = []
        
        for habit in habits:
            # Skip if habit is None
            if habit is None:
                continue
            if habit.is_subscription_like and habit.frequency_days < 30:
                # Skip if item_name is None
                if not habit.item_name:
                    continue
                    
                alternative = ""
                if "beef" in habit.item_name.lower() or "meat" in habit.item_name.lower():
                    alternative = "Plant-based meat alternatives"
                elif "dairy" in habit.item_name.lower():
                    alternative = "Plant-based dairy alternatives"
                elif "single-use" in habit.item_name.lower():
                    alternative = "Reusable alternatives"
                else:
                    alternative = f"Sustainable alternative to {habit.item_name}"
                
                subscriptions.append(SubscriptionToReplace(
                    item_name=habit.item_name,
                    frequency=f"Every {habit.frequency_days} days",
                    annual_carbon_kg=habit.total_impact_annual_kg,
                    alternative=alternative,
                    potential_savings_kg=round(habit.total_impact_annual_kg * 0.4, 2)
                ))
        
        return subscriptions[:4]
    
    def _generate_daily_plan(
        self,
        num_days: int,
        problem_areas: List[CategoryAnalysis]
    ) -> List[SustainabilityPlanDay]:
        """Generate day-by-day plan"""
        plan = []
        
        focus_areas = [p.category for p in problem_areas]
        actions = {
            "food": [
                "Try a plant-based recipe from your recommendations",
                "Skip takeout, cook at home",
                "Buy local vegetables at farmer's market",
                "Meal prep with seasonal ingredients"
            ],
            "transport": [
                "Bike or walk for short trips",
                "Use public transit",
                "Carpool with a colleague",
                "Consolidate errands into one trip"
            ],
            "shopping": [
                "Buy secondhand clothing",
                "Repair an old item",
                "Skip non-essential purchases",
                "Choose items with minimal packaging"
            ],
            "energy": [
                "Use natural lighting during the day",
                "Turn off devices when not in use",
                "Lower thermostat by 2°C",
                "Take a shorter shower"
            ]
        }
        
        for day in range(1, num_days + 1):
            # Rotate through focus areas
            focus = focus_areas[(day - 1) % len(focus_areas)] if focus_areas else "food"
            area_actions = actions.get(focus, actions["food"])
            
            action = area_actions[(day - 1) % len(area_actions)]
            
            # Difficulty increases toward end of month
            if day <= 10:
                difficulty = "easy"
                savings = 0.5
            elif day <= 20:
                difficulty = "medium"
                savings = 1.0
            else:
                difficulty = "hard"
                savings = 1.5
            
            plan.append(SustainabilityPlanDay(
                day=day,
                focus_area=focus,
                action=action,
                carbon_saved_vs_typical_kg=round(savings, 2),
                difficulty_level=difficulty
            ))
        
        return plan
