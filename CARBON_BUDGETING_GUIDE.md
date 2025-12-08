# Carbon Budgeting AI + Sustainability Planner

## Complete API & Implementation Guide

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Backend API Endpoints](#backend-api-endpoints)
3. [Data Models](#data-models)
4. [Frontend Components](#frontend-components)
5. [Custom Hooks](#custom-hooks)
6. [Example Responses](#example-responses)
7. [Usage Examples](#usage-examples)

---

## Overview

The Carbon Budgeting AI module provides intelligent carbon footprint analysis, forecasting, and personalized sustainability recommendations. It includes:

- **Carbon Analytics**: Aggregate and analyze historical emissions data
- **Forecasting Engine**: Predict 30-day carbon footprint trends
- **Adaptive Coach**: Generate weekly carbon budgets with smart tradeoffs
- **Lifestyle Simulator**: Show impact of lifestyle changes
- **Sustainability Planner**: Create 30-day personalized action plans
- **Recipe Database**: Low-carbon meal suggestions
- **Commute Optimizer**: Alternative transportation options

---

## Backend API Endpoints

### 1. GET `/api/carbon/insights`

Get comprehensive carbon footprint analysis.

**Query Parameters:**

- `period` (string): "day", "week", or "month" (default: "month")

**Response:**

```json
{
  "summary": "Your monthly carbon footprint is 45.2 kg CO2...",
  "total_footprint_kg": 45.2,
  "period": "month",
  "average_daily_kg": 1.45,
  "category_breakdown": [
    {
      "category": "food",
      "total_kg": 28.5,
      "percentage": 63.0,
      "item_count": 45,
      "avg_per_item": 0.63
    },
    {
      "category": "transport",
      "total_kg": 12.3,
      "percentage": 27.2,
      "item_count": 8,
      "avg_per_item": 1.54
    }
  ],
  "top_5_sources": [
    {
      "item": "beef",
      "total_kg": 12.5,
      "frequency": 8,
      "avg_per_purchase_kg": 1.56
    }
  ],
  "recurring_patterns": [
    {
      "item": "beef",
      "frequency_days": 7,
      "annual_impact_kg": 81.2,
      "is_subscription_like": true
    }
  ]
}
```

---

### 2. GET `/api/carbon/forecast`

Get 30-day carbon emissions forecast with trend analysis.

**Query Parameters:**

- `days` (integer): Number of days to forecast, max 90 (default: 30)

**Response:**

```json
{
  "forecast_days": 30,
  "forecasts": [
    {
      "date": "2025-12-09",
      "predicted_kg": 1.45,
      "confidence_interval": [0.95, 1.95],
      "trend": "stable"
    },
    {
      "date": "2025-12-10",
      "predicted_kg": 1.52,
      "confidence_interval": [1.0, 2.04],
      "trend": "increasing"
    }
  ],
  "summary": "Your emissions are projected to be low over the next 30 days.",
  "risk_level": "low"
}
```

---

### 3. POST `/api/carbon/simulate`

Simulate carbon impact of lifestyle changes.

**Request Body:**

```json
{
  "change_type": "diet",
  "parameters": {
    "reduction_percent": 50
  }
}
```

**Change Types:**

#### Diet Change

```json
{
  "change_type": "diet",
  "parameters": {
    "reduction_percent": 30 // 0-100, reduction in meat consumption
  }
}
```

#### Commute Change

```json
{
  "change_type": "commute",
  "parameters": {
    "from_mode": "car", // car, public_transit, carpool, bike, walk
    "to_mode": "bike",
    "days_per_week": 5 // 1-7
  }
}
```

#### Shopping Change

```json
{
  "change_type": "shopping",
  "parameters": {
    "reduction_percent": 30 // Reduce new purchases by X%
  }
}
```

#### Energy Change

```json
{
  "change_type": "energy",
  "parameters": {
    "efficiency_improvement_percent": 20 // 0-50
  }
}
```

**Response:**

```json
{
  "change_description": "Reducing meat consumption by 50%",
  "estimated_reduction_kg": 2.15,
  "estimated_reduction_percent": 37.5,
  "annual_impact_kg": 784.75,
  "affected_categories": ["food"]
}
```

---

### 4. GET `/api/carbon/coach`

Get adaptive weekly carbon budget and recommendations.

**Response:**

```json
{
  "week_start_date": "2025-12-08",
  "week_end_date": "2025-12-14",
  "recommended_weekly_limit_kg": 9.15,
  "recommended_daily_limit_kg": 1.31,
  "historical_weekly_avg": 10.75,
  "progress_percent": 45.5,
  "tradeoff_suggestions": [
    "If you buy beef twice this week, skip the takeout meals to stay under budget.",
    "Choosing plant-based proteins for 3 meals saves ~1.5 kg CO2 this week.",
    "Buying local vegetables instead of imported ones saves ~0.8 kg CO2."
  ]
}
```

---

### 5. GET `/api/carbon/plan/30-day`

Generate comprehensive 30-day personalized sustainability plan.

**Response:**

```json
{
  "start_date": "2025-12-08",
  "end_date": "2026-01-06",
  "current_weekly_avg_kg": 10.75,
  "target_weekly_avg_kg": 9.15,
  "total_potential_savings_kg": 6.4,
  "summary": "Your current weekly footprint is 10.75 kg CO2. Over 30 days, we can reduce this...",
  "problem_areas": [
    {
      "category": "food",
      "total_kg": 28.5,
      "percentage": 63.0,
      "item_count": 45,
      "avg_per_item": 0.63
    }
  ],
  "improvement_checklist": [
    "✓ Try 2 meatless days this week",
    "✓ Buy local and seasonal produce",
    "✓ Reduce single-use food packaging"
  ],
  "recipes": [
    {
      "name": "Lentil Buddha Bowl",
      "carbon_footprint_kg": 0.8,
      "protein_g": 15,
      "prep_time_minutes": 20,
      "ingredients": [
        "lentils",
        "quinoa",
        "roasted vegetables",
        "tahini dressing"
      ],
      "savings_vs_typical_kg": 2.1
    }
  ],
  "commute_alternatives": [
    {
      "mode": "Electric Bike",
      "annual_carbon_kg": 7.3,
      "cost_per_month": 50,
      "time_per_day_minutes": 18,
      "feasibility_score": 7.5
    }
  ],
  "habit_changes": [
    "Replace beef with plant-based meat alternatives (saves ~50 kg CO2/year)"
  ],
  "subscriptions_to_replace": [
    {
      "item_name": "beef",
      "frequency": "Every 7 days",
      "annual_carbon_kg": 81.2,
      "alternative": "Plant-based meat alternatives",
      "potential_savings_kg": 32.48
    }
  ],
  "daily_plan": [
    {
      "day": 1,
      "focus_area": "food",
      "action": "Try a plant-based recipe from your recommendations",
      "carbon_saved_vs_typical_kg": 0.5,
      "difficulty_level": "easy"
    }
  ]
}
```

---

## Data Models

### Database Tables (SQLAlchemy)

```python
# Carbon Goals
class CarbonGoal(Base):
    id: int
    user_id: int (FK)
    weekly_limit_kg: float
    daily_limit_kg: float
    reduction_target_percent: float = 15.0
    created_at: datetime
    updated_at: datetime

# 30-Day Plans
class SustainabilityPlan(Base):
    id: int
    user_id: int (FK)
    start_date: datetime
    end_date: datetime
    current_weekly_avg_kg: float
    target_weekly_avg_kg: float
    total_potential_savings_kg: float
    summary: str
    created_at: datetime

# Daily Actions
class DailyPlanAction(Base):
    id: int
    plan_id: int (FK)
    day: int
    focus_area: str
    action: str
    carbon_saved_kg: float (nullable)
    difficulty_level: str  # easy, medium, hard
    completed: int (0 or 1)
```

### Python Dataclasses (carbon_budgeting.py)

```python
@dataclass
class DailyFootprint:
    date: str
    total_kg: float
    category_breakdown: Dict[str, float]
    item_count: int

@dataclass
class CategoryAnalysis:
    category: str
    total_kg: float
    percentage: float
    item_count: int
    avg_per_item: float

@dataclass
class SimulationResult:
    change_description: str
    estimated_reduction_kg: float
    estimated_reduction_percent: float
    annual_impact_kg: float
    affected_categories: List[str]

@dataclass
class ThirtyDayPlan:
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
```

---

## Frontend Components

### 1. CarbonCoachCard

Displays weekly budget and adaptive tradeoff recommendations.

```jsx
import { CarbonCoachCard } from "./components/CarbonCoach";

function Dashboard() {
  return <CarbonCoachCard />;
}
```

**Features:**

- Weekly budget visualization
- Progress bar
- Smart tradeoff suggestions
- Status messages (on track, approaching limit, exceeded)

### 2. ForecastGraph

Visualizes 30-day carbon forecast with confidence intervals.

```jsx
import { ForecastGraph } from "./components/ForecastGraph";

function Dashboard() {
  return <ForecastGraph />;
}
```

**Features:**

- 4 weeks of daily predictions
- Hover tooltips with details
- Trend indicators (increasing, stable, decreasing)
- Risk level badge

### 3. SimulationTool

Interactive what-if simulator for lifestyle changes.

```jsx
import { SimulationTool } from "./components/SimulationTool";

function Dashboard() {
  return <SimulationTool />;
}
```

**Features:**

- 4 change types: Diet, Commute, Shopping, Energy
- Interactive parameter adjustment
- Impact summary with annual calculations
- Real-world comparisons (flights, tree equivalents)

### 4. ThirtyDayPlanView

Comprehensive 30-day sustainability plan with multiple tabs.

```jsx
import { ThirtyDayPlanView } from "./components/ThirtyDayPlanView";

function Dashboard() {
  return <ThirtyDayPlanView />;
}
```

**Tabs:**

- Overview: Problem areas and checklist
- Daily Plan: Calendar-style action tracker
- Recipes: Low-carbon meal suggestions
- Commute: Transportation alternatives
- Habits: Recurring purchases to replace

---

## Custom Hooks

### useCarbonInsights

```jsx
const { insights, loading, error } = useCarbonInsights(period);
// period: "day", "week", "month"
```

### useCarbonForecast

```jsx
const { forecast, loading, error } = useCarbonForecast(days);
// days: 1-90
```

### useCarbonCoach

```jsx
const { budget, loading, error } = useCarbonCoach();
```

### useThirtyDayPlan

```jsx
const { plan, loading, error } = useThirtyDayPlan();
```

### useSimulation

```jsx
const { simulate, loading, error } = useSimulation();
const result = await simulate("diet", { reduction_percent: 50 });
```

### useCarbonDashboard (combined)

```jsx
const { insights, forecast, budget, plan, loading, error } =
  useCarbonDashboard();
```

---

## Example Responses

### Real-World Scenario: College Student

**Current Footprint:**

```
Weekly Average: 12.5 kg CO2
- Food: 8.2 kg (66%) - lots of takeout, occasional meat
- Transport: 3.1 kg (25%) - drives to campus
- Shopping: 1.2 kg (9%) - occasional purchases
```

**Insights Response:**

```json
{
  "summary": "Your primary carbon source is food (66%), driven by takeout and meat consumption. Making dietary changes would have the biggest impact.",
  "average_daily_kg": 1.79,
  "category_breakdown": [
    { "category": "food", "total_kg": 116.5, "percentage": 66.0 },
    { "category": "transport", "total_kg": 44.2, "percentage": 25.0 },
    { "category": "shopping", "total_kg": 16.0, "percentage": 9.0 }
  ],
  "recurring_patterns": [
    {
      "item": "pizza",
      "frequency_days": 7,
      "annual_impact_kg": 43.6,
      "is_subscription_like": true
    }
  ]
}
```

**Simulation Result (Diet Change):**

```json
{
  "change_description": "Reducing meat consumption by 50%",
  "estimated_reduction_kg": 2.1,
  "estimated_reduction_percent": 35.0,
  "annual_impact_kg": 766.5,
  "affected_categories": ["food"]
}
// Result: 12.5 kg/week → 10.4 kg/week (-1.68%/week × 52 weeks)
```

**30-Day Plan Summary:**

```json
{
  "current_weekly_avg_kg": 12.5,
  "target_weekly_avg_kg": 10.625,
  "total_potential_savings_kg": 7.5,
  "summary": "Your top opportunity is reducing meat/takeout. Cycling to campus 2-3x/week saves additional carbon.",
  "problem_areas": [
    { "category": "food", "percentage": 66.0 },
    { "category": "transport", "percentage": 25.0 },
    { "category": "shopping", "percentage": 9.0 }
  ],
  "improvement_checklist": [
    "✓ Try 3 meatless dinners this week",
    "✓ Bike or walk to campus 2x per week",
    "✓ Pack lunch instead of buying takeout (save $50/week + 1.5kg CO2)"
  ]
}
```

---

## Usage Examples

### Example 1: Integrating into Main Dashboard

```jsx
// App.jsx or Dashboard.jsx
import { CarbonCoachCard } from "./components/CarbonCoach";
import { ForecastGraph } from "./components/ForecastGraph";
import { SimulationTool } from "./components/SimulationTool";
import { ThirtyDayPlanView } from "./components/ThirtyDayPlanView";

export function CarbonDashboard() {
  return (
    <div className="carbon-dashboard">
      <CarbonCoachCard />
      <ForecastGraph />
      <SimulationTool />
      <ThirtyDayPlanView />
    </div>
  );
}
```

### Example 2: Custom Data Fetching

```jsx
import { useCarbonInsights } from "./hooks/useCarbonBudgeting";

function CarbonMetrics() {
  const { insights, loading, error } = useCarbonInsights("month");

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>{insights.average_daily_kg} kg CO2/day</h2>
      {insights.category_breakdown.map((cat) => (
        <div key={cat.category}>
          {cat.category}: {cat.percentage}%
        </div>
      ))}
    </div>
  );
}
```

### Example 3: Using Simulation Hook

```jsx
function UserSimulation() {
  const { simulate, loading } = useSimulation();
  const [result, setResult] = useState(null);

  const handleSimulate = async () => {
    const res = await simulate("commute", {
      from_mode: "car",
      to_mode: "bike",
      days_per_week: 3,
    });
    setResult(res);
  };

  return (
    <div>
      <button onClick={handleSimulate} disabled={loading}>
        Calculate Impact
      </button>
      {result && <p>Annual Savings: {result.annual_impact_kg} kg CO2</p>}
    </div>
  );
}
```

---

## File Structure

```
backend/
  app/
    carbon_budgeting.py          # Main analytics engines
    models.py                     # DB models (updated)
    schemas.py                    # Pydantic schemas (updated)
    main.py                       # API endpoints (updated)

app/
  src/
    components/
      CarbonCoach.jsx             # Coach component
      CarbonCoach.css
      ForecastGraph.jsx           # Forecast component
      ForecastGraph.css
      SimulationTool.jsx          # Simulator component
      SimulationTool.css
      ThirtyDayPlanView.jsx       # Plan view component
      ThirtyDayPlanView.css
    hooks/
      useCarbonBudgeting.js       # Custom hooks
```

---

## Dependencies

### Backend (Python)

- fastapi
- sqlalchemy
- pydantic
- pandas
- numpy
- python-dateutil

All included in `requirements.txt`

### Frontend (React)

- react (existing)
- react-dom (existing)
- fetch API (built-in)

No new dependencies required!

---

## Security Considerations

1. **Authentication**: All endpoints require Bearer token auth
2. **User Isolation**: Data filtered by `current_user.id`
3. **Input Validation**: Pydantic validates all inputs
4. **Rate Limiting**: Consider adding to prevent abuse
5. **HTTPS**: Use in production

---

## Performance Tips

1. **Caching**: Cache forecast results (regenerate daily)
2. **Lazy Loading**: Load plans only when needed
3. **Pagination**: Implement for large datasets
4. **Database Indexes**: Add indexes on `user_id`, `date`
5. **API Response Compression**: Gzip JSON responses

---

## Future Enhancements

1. Machine learning models for better forecasting
2. Social features (compare with friends)
3. Gamification (achievement badges, streaks)
4. Integration with calendar apps
5. Smart notifications (approaching budget, trend alerts)
6. CSV export of plans and recommendations
7. Mobile app with offline support
8. Carbon offset marketplace integration

---

Generated for CarbonDrop Sustainability App
