# 🌱 Carbon Budgeting AI - Quick Reference Card

## 🚀 Quick Start (5 Minutes)

```bash
# 1. Backend is ready - just run
cd backend
python -m uvicorn app.main:app --reload

# 2. Frontend components are ready - add to your app
# Import in App.jsx:
import { CarbonCoachCard } from './components/CarbonCoach';

# 3. Test an endpoint
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/carbon/insights?period=month
```

---

## 📋 API Endpoints Cheat Sheet

| Method | Endpoint                  | Purpose                     | Auth |
| ------ | ------------------------- | --------------------------- | ---- |
| GET    | `/api/carbon/insights`    | Carbon analysis & breakdown | ✅   |
| GET    | `/api/carbon/forecast`    | 30-day predictions          | ✅   |
| POST   | `/api/carbon/simulate`    | Lifestyle impact simulation | ✅   |
| GET    | `/api/carbon/coach`       | Weekly budget & tradeoffs   | ✅   |
| GET    | `/api/carbon/plan/30-day` | Full sustainability plan    | ✅   |

---

## 🎨 Components Quick Reference

```jsx
// 1. Coach Component - Weekly Budget
<CarbonCoachCard />

// 2. Forecast Graph - 30-Day Trend
<ForecastGraph />

// 3. Simulation Tool - What-If Analysis
<SimulationTool />

// 4. Plan View - 30-Day Action Plan
<ThirtyDayPlanView />
```

---

## 🎯 Simulation Examples

### Diet Change

```json
{
  "change_type": "diet",
  "parameters": { "reduction_percent": 50 }
}
```

**Result**: Avg 2.15 kg CO2 saved daily = 784.75 kg/year

### Commute Change

```json
{
  "change_type": "commute",
  "parameters": {
    "from_mode": "car",
    "to_mode": "bike",
    "days_per_week": 5
  }
}
```

**Result**: ~2 kg CO2 saved daily = 730 kg/year

### Shopping Change

```json
{
  "change_type": "shopping",
  "parameters": { "reduction_percent": 30 }
}
```

**Result**: 0.9 kg CO2 saved daily = 328 kg/year

### Energy Change

```json
{
  "change_type": "energy",
  "parameters": { "efficiency_improvement_percent": 20 }
}
```

**Result**: 0.5 kg CO2 saved daily = 182 kg/year

---

## 🎣 Custom Hooks Cheat Sheet

```javascript
// Get carbon analysis
const { insights, loading, error } = useCarbonInsights("month");

// Get 30-day forecast
const { forecast, loading, error } = useCarbonForecast(30);

// Get weekly budget
const { budget, loading, error } = useCarbonCoach();

// Get 30-day plan
const { plan, loading, error } = useThirtyDayPlan();

// Run simulation
const { simulate, loading, error } = useSimulation();
await simulate("diet", { reduction_percent: 30 });

// Get everything at once
const { insights, forecast, budget, plan, loading, error } =
  useCarbonDashboard();
```

---

## 📊 Sample JSON Responses

### Insights

```json
{
  "summary": "Your primary source is food (63%)",
  "average_daily_kg": 1.79,
  "category_breakdown": [
    { "category": "food", "percentage": 63.0, "total_kg": 116.5 },
    { "category": "transport", "percentage": 25.0, "total_kg": 44.2 }
  ]
}
```

### Budget

```json
{
  "recommended_weekly_limit_kg": 9.15,
  "recommended_daily_limit_kg": 1.31,
  "progress_percent": 45.5,
  "tradeoff_suggestions": [
    "If you buy beef twice, skip takeout to stay under budget"
  ]
}
```

### Simulation

```json
{
  "change_description": "Reducing meat by 50%",
  "estimated_reduction_kg": 2.15,
  "estimated_reduction_percent": 37.5,
  "annual_impact_kg": 784.75
}
```

---

## 🗂️ File Locations

| File                                       | Purpose             | Size       |
| ------------------------------------------ | ------------------- | ---------- |
| `backend/app/carbon_budgeting.py`          | All engines & logic | 650+ lines |
| `backend/app/models.py`                    | Database tables     | +50 lines  |
| `backend/app/schemas.py`                   | API validation      | +200 lines |
| `backend/app/main.py`                      | API endpoints       | +500 lines |
| `app/src/components/CarbonCoach.jsx`       | Budget component    | 260 lines  |
| `app/src/components/ForecastGraph.jsx`     | Forecast component  | 320 lines  |
| `app/src/components/SimulationTool.jsx`    | Simulator component | 340 lines  |
| `app/src/components/ThirtyDayPlanView.jsx` | Plan component      | 520 lines  |
| `app/src/hooks/useCarbonBudgeting.js`      | Data hooks          | 200+ lines |

---

## 🔧 Configuration

### Environment Variables

```env
# .env (in app/ directory)
REACT_APP_API_URL=http://localhost:8000

# Production
REACT_APP_API_URL=https://api.yourdomain.com
```

### Database

```python
# Already configured in models.py
# Just run:
models.Base.metadata.create_all(bind=database.engine)
```

---

## ✅ Testing

```bash
# Test 1: Get insights
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/carbon/insights?period=month"

# Test 2: Get forecast
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/carbon/forecast?days=30"

# Test 3: Simulate diet change
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"change_type":"diet","parameters":{"reduction_percent":30}}' \
  "http://localhost:8000/api/carbon/simulate"

# Test 4: Get coach budget
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/carbon/coach"

# Test 5: Get 30-day plan
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/carbon/plan/30-day"
```

---

## 🎨 Component Usage

```jsx
// Complete dashboard
import React from "react";
import { CarbonCoachCard } from "./components/CarbonCoach";
import { ForecastGraph } from "./components/ForecastGraph";
import { SimulationTool } from "./components/SimulationTool";
import { ThirtyDayPlanView } from "./components/ThirtyDayPlanView";

export function CarbonDashboard() {
  return (
    <div className="carbon-dashboard">
      <h1>🌱 Carbon Budgeting AI</h1>
      <CarbonCoachCard /> {/* Weekly budget */}
      <ForecastGraph /> {/* 30-day trend */}
      <SimulationTool /> {/* What-if simulator */}
      <ThirtyDayPlanView /> {/* Action plan */}
    </div>
  );
}
```

---

## 🚀 Deployment

```bash
# Backend
cd backend
gunicorn app.main:app --workers 4 --bind 0.0.0.0:8000

# Frontend
cd app
npm run build
# Deploy build/ folder to static hosting
```

---

## 📚 Full Documentation

- **API Guide**: `CARBON_BUDGETING_GUIDE.md`
- **Integration Guide**: `INTEGRATION_GUIDE.md`
- **Project Summary**: `PROJECT_SUMMARY.md`

---

## 🎯 Key Metrics

**What You Get:**

- 5 REST API endpoints
- 4 React components
- 5+ custom hooks
- 3 database tables
- 8 low-carbon recipes
- 5 commute alternatives
- 2500+ lines of code
- 700+ lines of documentation

**Time to Value:**

- Setup: 15 minutes
- Integration: 2 hours
- Full deployment: 4 hours

---

## 🆘 Quick Troubleshooting

| Problem          | Solution                            |
| ---------------- | ----------------------------------- |
| 401 Unauthorized | Check auth token in localStorage    |
| CORS Error       | Verify backend CORS allows origin   |
| No data          | Upload receipts first, then refresh |
| Slow load        | Check database indexes, add caching |
| Mobile issues    | Clear browser cache, check viewport |

---

## 🔑 Key Features

✅ Intelligent forecasting (time-series)
✅ Adaptive budgeting (learns from history)
✅ Smart simulations (realistic impact)
✅ Personalized plans (30-day actions)
✅ Habit detection (recurring patterns)
✅ Recipe suggestions (8 low-carbon meals)
✅ Commute options (5 alternatives)
✅ Mobile responsive (all devices)
✅ Production ready (error handling, validation)
✅ Well documented (guides + code comments)

---

## 🎓 Architecture

```
User Receipts
    ↓
Analytics Engine (aggregate, analyze)
    ↓
Forecasting Engine (predict trends)
    ↓
Carbon Coach (weekly budgets)
    ↓
Simulator (what-if analysis)
    ↓
Plan Generator (30-day plan)
    ↓
API Response
    ↓
React Components + Hooks
    ↓
Beautiful Dashboard UI
```

---

## 💡 Tips & Tricks

1. **Cache forecasts**: Regenerate only daily to save resources
2. **Lazy load components**: Load tabs only when clicked
3. **Pre-generate plans**: Generate on upload, store in DB
4. **Monitor performance**: Track API response times
5. **A/B test simulations**: See which changes resonate
6. **Gamify**: Add badges for hitting goals
7. **Social**: Compare with friends/groups
8. **Export**: Allow PDF download of plans

---

## 📞 Support

**For Questions:**

1. Check documentation files
2. Review component source code
3. Look at example responses
4. Check backend logs

**Files:**

- `CARBON_BUDGETING_GUIDE.md` - API reference
- `INTEGRATION_GUIDE.md` - How to integrate
- `PROJECT_SUMMARY.md` - Complete overview
- Component JSX files - Implementation examples

---

**You're all set! 🚀 Start integrating and building sustainable futures!**

Last updated: December 8, 2025
