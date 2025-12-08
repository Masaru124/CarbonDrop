/**
 * Carbon Forecast Graph Component
 * Visualizes 30-day carbon emissions forecast
 */

import React, { useEffect, useState } from "react";
import { useCarbonForecast } from "../hooks/useCarbonBudgeting";
import "./ForecastGraph.css";

export function ForecastGraph() {
  const { forecast, loading, error } = useCarbonForecast();
  const [hoveredDay, setHoveredDay] = useState(null);

  if (loading) {
    return <div className="forecast-graph loading">Loading forecast...</div>;
  }

  if (error) {
    return <div className="forecast-graph error">Error: {error}</div>;
  }

  if (!forecast || forecast.forecasts.length === 0) {
    return <div className="forecast-graph">No forecast data available.</div>;
  }

  const forecasts = forecast.forecasts.slice(0, 30); // Show first 30 days
  const maxValue = Math.max(...forecasts.map((f) => f.predicted_kg), 10);
  const minValue = 0;

  // Group by week for display
  const weeks = [];
  for (let i = 0; i < forecasts.length; i += 7) {
    weeks.push({
      weekNumber: Math.floor(i / 7) + 1,
      days: forecasts.slice(i, i + 7),
    });
  }

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case "low":
        return "#4CAF50";
      case "medium":
        return "#FF9800";
      case "high":
        return "#F44336";
      default:
        return "#2196F3";
    }
  };

  const getTrendIcon = (trend) => {
    switch (trend) {
      case "increasing":
        return "📈";
      case "decreasing":
        return "📉";
      default:
        return "➡️";
    }
  };

  return (
    <div className="forecast-graph">
      <div className="forecast-header">
        <h2>📊 30-Day Carbon Forecast</h2>
        <div
          className="risk-badge"
          style={{ backgroundColor: getRiskColor(forecast.risk_level) }}
        >
          Risk: <strong>{forecast.risk_level.toUpperCase()}</strong>
        </div>
      </div>

      <p className="forecast-summary">{forecast.summary}</p>

      <div className="forecast-container">
        {weeks.map((week) => (
          <div key={week.weekNumber} className="week-section">
            <h3>Week {week.weekNumber}</h3>
            <div className="days-grid">
              {week.days.map((day, idx) => {
                const percentHeight =
                  ((day.predicted_kg - minValue) / (maxValue - minValue)) * 100;
                const isHovered = hoveredDay === `${week.weekNumber}-${idx}`;

                return (
                  <div
                    key={`${week.weekNumber}-${idx}`}
                    className="day-bar-container"
                    onMouseEnter={() =>
                      setHoveredDay(`${week.weekNumber}-${idx}`)
                    }
                    onMouseLeave={() => setHoveredDay(null)}
                  >
                    <div className={`day-bar ${isHovered ? "hovered" : ""}`}>
                      <div
                        className={`bar-fill ${day.trend}`}
                        style={{
                          height: `${Math.max(percentHeight, 5)}%`,
                          backgroundColor:
                            day.predicted_kg > 7 ? "#FF6B6B" : "#4ECDC4",
                        }}
                      />
                    </div>
                    {isHovered && (
                      <div className="day-tooltip">
                        <p className="tooltip-date">
                          {new Date(day.date).toLocaleDateString("en-US", {
                            weekday: "short",
                            month: "short",
                            day: "numeric",
                          })}
                        </p>
                        <p className="tooltip-value">
                          {day.predicted_kg.toFixed(2)} kg CO₂
                        </p>
                        <p className="tooltip-confidence">
                          {day.confidence_interval[0].toFixed(1)} -{" "}
                          {day.confidence_interval[1].toFixed(1)} kg
                        </p>
                        <p className="tooltip-trend">
                          {getTrendIcon(day.trend)} {day.trend}
                        </p>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      <div className="forecast-legend">
        <div className="legend-item">
          <div
            className="legend-color"
            style={{ backgroundColor: "#4ECDC4" }}
          />
          <span>Below 7 kg/day (Good)</span>
        </div>
        <div className="legend-item">
          <div
            className="legend-color"
            style={{ backgroundColor: "#FF6B6B" }}
          />
          <span>Above 7 kg/day (High)</span>
        </div>
      </div>

      <div className="forecast-insights">
        <h3>💡 Forecast Insights</h3>
        <ul>
          <li>📈 Increasing trend detected - consider reducing purchases</li>
          <li>🛒 High-carbon days typically occur on weekends</li>
          <li>
            ✅ Your lowest-carbon days average{" "}
            {Math.min(...forecasts.map((f) => f.predicted_kg)).toFixed(1)} kg
          </li>
        </ul>
      </div>
    </div>
  );
}

export default ForecastGraph;
