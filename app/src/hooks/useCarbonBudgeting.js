import { useState, useEffect, useCallback } from "react";
import { api } from "../lib/api";

function useFetch(endpoint) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    api
      .get(endpoint)
      .then((d) => {
        if (!cancelled) {
          setData(d);
          setError(null);
        }
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, [endpoint]);

  return { data, loading, error };
}

export function useCarbonInsights(period = "month") {
  const { data, loading, error } = useFetch(`/api/carbon/insights?period=${period}`);
  return { insights: data, loading, error };
}

export function useCarbonForecast(days = 30) {
  const { data, loading, error } = useFetch(`/api/carbon/forecast?days=${days}`);
  return { forecast: data, loading, error };
}

export function useCarbonCoach() {
  const { data, loading, error } = useFetch("/api/carbon/coach");
  return { budget: data, loading, error };
}

export function useThirtyDayPlan() {
  const { data, loading, error } = useFetch("/api/carbon/plan/30-day");
  return { plan: data, loading, error };
}

export function useSimulation() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const simulate = useCallback(async (changeType, parameters) => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.post("/api/carbon/simulate", {
        change_type: changeType,
        parameters,
      });
      return data;
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return { simulate, loading, error };
}

export function useCarbonDashboard() {
  const insights = useCarbonInsights();
  const forecast = useCarbonForecast();
  const budget = useCarbonCoach();
  const plan = useThirtyDayPlan();
  const simulation = useSimulation();

  const loading = insights.loading || forecast.loading || budget.loading || plan.loading;
  const error = insights.error || forecast.error || budget.error || plan.error;

  const insightsNormalized = insights.insights
    ? {
        ...insights.insights,
        average_daily_footprint: insights.insights.average_daily_kg || insights.insights.average_daily || null,
        total_footprint: insights.insights.total_footprint_kg || null,
      }
    : null;

  const forecastNormalized = forecast.forecast
    ? {
        ...forecast.forecast,
        projected_monthly_total:
          Array.isArray(forecast.forecast.forecasts) && forecast.forecast.forecasts.length
            ? forecast.forecast.forecasts.reduce((s, d) => s + (d.predicted_kg || 0), 0)
            : null,
      }
    : null;

  const coachNormalized = budget.budget
    ? {
        ...budget.budget,
        weekly_budget: budget.budget.recommended_weekly_limit_kg || budget.budget.weekly_budget || null,
        daily_budget: budget.budget.recommended_daily_limit_kg || budget.budget.daily_budget || null,
      }
    : null;

  return {
    insights: insightsNormalized,
    forecast: forecastNormalized,
    coach: coachNormalized,
    thirtyDayPlan: plan.plan ? { ...plan.plan } : null,
    loading,
    error,
    runSimulation: simulation.simulate,
    simulationResult: null,
    simulationLoading: simulation.loading,
    simulationError: simulation.error,
  };
}
