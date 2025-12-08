/**
 * Carbon Coach Component
 * Displays weekly carbon budget and adaptive recommendations
 */

import React, { useEffect, useState } from "react";
import { useCarbonCoach } from "../hooks/useCarbonBudgeting";
import "./CarbonCoach.css";

export function CarbonCoachCard() {
  const { budget, loading, error } = useCarbonCoach();

  if (loading) {
    return (
      <div className="carbon-coach-card loading">
        Loading coach recommendations...
      </div>
    );
  }

  if (error) {
    return <div className="carbon-coach-card error">Error: {error}</div>;
  }

  if (!budget) {
    return (
      <div className="carbon-coach-card">
        Upload receipts to get personalized recommendations.
      </div>
    );
  }

  const statusColor =
    budget.progress_percent <= 50
      ? "green"
      : budget.progress_percent <= 100
      ? "yellow"
      : "red";

  return (
    <div className="carbon-coach-card">
      <h2>🧠 Your Carbon Coach</h2>

      <div className="week-overview">
        <div className="week-info">
          <p className="week-dates">
            {new Date(budget.week_start_date).toLocaleDateString()} -{" "}
            {new Date(budget.week_end_date).toLocaleDateString()}
          </p>
        </div>

        <div className="budget-targets">
          <div className="budget-item">
            <label>Weekly Limit</label>
            <p className="target">
              {budget.recommended_weekly_limit_kg} kg CO₂
            </p>
          </div>
          <div className="budget-item">
            <label>Daily Limit</label>
            <p className="target">{budget.recommended_daily_limit_kg} kg CO₂</p>
          </div>
          <div className="budget-item">
            <label>Last Week Avg</label>
            <p className="historical">{budget.historical_weekly_avg} kg CO₂</p>
          </div>
        </div>

        <div className="progress-bar-container">
          <label>Weekly Progress</label>
          <div className="progress-bar">
            <div
              className={`progress-fill ${statusColor}`}
              style={{ width: `${Math.min(budget.progress_percent, 100)}%` }}
            />
          </div>
          <p className="progress-text">
            {budget.progress_percent.toFixed(1)}% of budget used
          </p>
        </div>
      </div>

      <div className="tradeoffs-section">
        <h3>💡 Smart Tradeoffs</h3>
        <ul className="tradeoffs-list">
          {budget.tradeoff_suggestions &&
            budget.tradeoff_suggestions.map((suggestion, idx) => (
              <li key={idx} className="tradeoff-item">
                {suggestion}
              </li>
            ))}
        </ul>
      </div>

      <div className="coach-message">
        {budget.progress_percent <= 50 && (
          <p className="positive">
            ✨ Great job! You're well under your budget. Keep it up!
          </p>
        )}
        {budget.progress_percent > 50 && budget.progress_percent <= 80 && (
          <p className="neutral">
            📊 You're on track. Focus on the tradeoffs above to stay within
            budget.
          </p>
        )}
        {budget.progress_percent > 80 && budget.progress_percent < 100 && (
          <p className="warning">
            ⚠️ You're approaching your budget. Make mindful choices for the rest
            of the week.
          </p>
        )}
        {budget.progress_percent >= 100 && (
          <p className="alert">
            🚨 You've exceeded your budget. Check out the recommendations below!
          </p>
        )}
      </div>
    </div>
  );
}

export default CarbonCoachCard;
