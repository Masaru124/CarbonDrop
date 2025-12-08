/**
 * Custom Hooks for Carbon Budgeting AI Module
 * Manages data fetching and state for all carbon budgeting features
 */

import { useState, useEffect } from "react";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Hook for carbon insights
export function useCarbonInsights(period = "month") {
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchInsights = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem("token");
        const response = await fetch(
          `${API_BASE_URL}/api/carbon/insights?period=${period}`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
              "Content-Type": "application/json",
            },
          }
        );

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        setInsights(data);
        setError(null);
      } catch (err) {
        setError(err.message);
        setInsights(null);
      } finally {
        setLoading(false);
      }
    };

    fetchInsights();
  }, [period]);

  return { insights, loading, error };
}

// Hook for carbon forecast
export function useCarbonForecast(days = 30) {
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchForecast = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem("token");
        const response = await fetch(
          `${API_BASE_URL}/api/carbon/forecast?days=${days}`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
              "Content-Type": "application/json",
            },
          }
        );

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        setForecast(data);
        setError(null);
      } catch (err) {
        setError(err.message);
        setForecast(null);
      } finally {
        setLoading(false);
      }
    };

    fetchForecast();
  }, [days]);

  return { forecast, loading, error };
}

// Hook for carbon coach budget
export function useCarbonCoach() {
  const [budget, setBudget] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchBudget = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem("token");
        const response = await fetch(`${API_BASE_URL}/api/carbon/coach`, {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        setBudget(data);
        setError(null);
      } catch (err) {
        setError(err.message);
        setBudget(null);
      } finally {
        setLoading(false);
      }
    };

    fetchBudget();
  }, []);

  return { budget, loading, error };
}

// Hook for 30-day plan
export function useThirtyDayPlan() {
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPlan = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem("token");
        const response = await fetch(`${API_BASE_URL}/api/carbon/plan/30-day`, {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        setPlan(data);
        setError(null);
      } catch (err) {
        setError(err.message);
        setPlan(null);
      } finally {
        setLoading(false);
      }
    };

    fetchPlan();
  }, []);

  return { plan, loading, error };
}

// Hook for lifestyle simulation
export function useSimulation() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const simulate = async (changeType, parameters) => {
    try {
      setLoading(true);
      setError(null);

      const token = localStorage.getItem("token");
      const response = await fetch(`${API_BASE_URL}/api/carbon/simulate`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          change_type: changeType,
          parameters: parameters,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  };

  return { simulate, loading, error };
}

// Combined hook for dashboard
export function useCarbonDashboard() {
  const insights = useCarbonInsights();
  const forecast = useCarbonForecast();
  const budget = useCarbonCoach();
  const plan = useThirtyDayPlan();
  const simulation = useSimulation();

  const loading =
    insights.loading || forecast.loading || budget.loading || plan.loading;
  const error = insights.error || forecast.error || budget.error || plan.error;
  // Normalize backend responses to the shapes UI expects
  const insightsNormalized = insights.insights
    ? {
        ...insights.insights,
        average_daily_footprint:
          insights.insights.average_daily_kg ||
          insights.insights.average_daily ||
          null,
        total_footprint:
          insights.insights.total_footprint_kg ||
          insights.insights.total_footprint_kg ||
          null,
      }
    : null;

  const forecastNormalized = forecast.forecast
    ? {
        ...forecast.forecast,
        // keep original fields but add a projected monthly total (sum of 30-day predictions)
        projected_monthly_total:
          Array.isArray(forecast.forecast.forecasts) &&
          forecast.forecast.forecasts.length
            ? forecast.forecast.forecasts.reduce(
                (s, d) => s + (d.predicted_kg || 0),
                0
              )
            : null,
      }
    : null;

  const coachNormalized = budget.budget
    ? {
        ...budget.budget,
        // some components expect `weekly_budget` and `daily_budget` keys
        weekly_budget:
          budget.budget.recommended_weekly_limit_kg ||
          budget.budget.weekly_budget ||
          null,
        daily_budget:
          budget.budget.recommended_daily_limit_kg ||
          budget.budget.daily_budget ||
          null,
      }
    : null;

  const planNormalized = plan.plan ? { ...plan.plan } : null;

  return {
    insights: insightsNormalized,
    forecast: forecastNormalized,
    coach: coachNormalized,
    thirtyDayPlan: planNormalized,
    loading,
    error,
    runSimulation: simulation.simulate,
    simulationResult: null,
    simulationLoading: simulation.loading,
    simulationError: simulation.error,
  };
}

// Utility hook for refreshing data
export function useRefreshData() {
  const refreshInsights = (period) => {
    // Trigger refetch by key change
    return useCarbonInsights(period);
  };

  const refreshForecast = (days) => {
    return useCarbonForecast(days);
  };

  const refreshBudget = () => {
    return useCarbonCoach();
  };

  const refreshPlan = () => {
    return useThirtyDayPlan();
  };

  return {
    refreshInsights,
    refreshForecast,
    refreshBudget,
    refreshPlan,
  };
}
