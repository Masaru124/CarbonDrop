/**
 * 30-Day Plan View Component
 * Displays comprehensive sustainability plan with daily actions
 */

import React, { useEffect, useState } from "react";
import { useThirtyDayPlan } from "../hooks/useCarbonBudgeting";
import "./ThirtyDayPlanView.css";

export function ThirtyDayPlanView() {
  const { plan, loading, error } = useThirtyDayPlan();
  const [expandedDay, setExpandedDay] = useState(null);
  const [activeTab, setActiveTab] = useState("overview");
  const [completedDays, setCompletedDays] = useState(new Set());

  const toggleDayCompletion = (day) => {
    const newCompleted = new Set(completedDays);
    if (newCompleted.has(day)) {
      newCompleted.delete(day);
    } else {
      newCompleted.add(day);
    }
    setCompletedDays(newCompleted);
  };

  if (loading) {
    return (
      <div className="plan-view loading">
        Generating your personalized plan...
      </div>
    );
  }

  if (error) {
    return <div className="plan-view error">Error: {error}</div>;
  }

  if (!plan) {
    return (
      <div className="plan-view">No plan available. Upload receipts first.</div>
    );
  }

  const completionPercent = (completedDays.size / 30) * 100;

  const getDifficultyColor = (level) => {
    switch (level) {
      case "easy":
        return "#4CAF50";
      case "medium":
        return "#FF9800";
      case "hard":
        return "#F44336";
      default:
        return "#2196F3";
    }
  };

  return (
    <div className="plan-view">
      <div className="plan-header">
        <h1>🌱 Your 30-Day Sustainability Plan</h1>
        <p className="dates">
          {new Date(plan.start_date).toLocaleDateString()} -{" "}
          {new Date(plan.end_date).toLocaleDateString()}
        </p>
      </div>

      <div className="plan-summary-box">
        <h2>Summary</h2>
        <p>{plan.summary}</p>

        <div className="target-metrics">
          <div className="metric">
            <label>Current Weekly Avg</label>
            <p className="value current">{plan.current_weekly_avg_kg} kg CO₂</p>
          </div>
          <div className="metric">
            <label>Target After 30 Days</label>
            <p className="value target">{plan.target_weekly_avg_kg} kg CO₂</p>
          </div>
          <div className="metric">
            <label>Potential Savings</label>
            <p className="value savings">
              {plan.total_potential_savings_kg} kg CO₂
            </p>
          </div>
        </div>
      </div>

      <div className="tabs">
        {["overview", "daily-plan", "recipes", "commute", "habits"].map(
          (tab) => (
            <button
              key={tab}
              className={`tab-button ${activeTab === tab ? "active" : ""}`}
              onClick={() => setActiveTab(tab)}
            >
              {tab.split("-").join(" ").toUpperCase()}
            </button>
          )
        )}
      </div>

      <div className="tab-content">
        {/* OVERVIEW TAB */}
        {activeTab === "overview" && (
          <div className="overview-section">
            <div className="problems-section">
              <h3>🎯 Top 3 Problem Areas</h3>
              <div className="problem-cards">
                {plan.problem_areas.map((area, idx) => (
                  <div key={idx} className="problem-card">
                    <h4>
                      {idx + 1}. {area.category.toUpperCase()}
                    </h4>
                    <p className="impact">{area.total_kg} kg CO₂</p>
                    <p className="percent">{area.percentage}% of total</p>
                    <p className="items">{area.item_count} items analyzed</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="checklist-section">
              <h3>✅ 30-Day Improvement Checklist</h3>
              <ul className="checklist">
                {plan.improvement_checklist.map((item, idx) => (
                  <li key={idx} className="checklist-item">
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* DAILY PLAN TAB */}
        {activeTab === "daily-plan" && (
          <div className="daily-plan-section">
            <div className="completion-progress">
              <label>Overall Progress</label>
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${completionPercent}%` }}
                />
              </div>
              <p className="progress-text">
                {completedDays.size} of 30 days completed
              </p>
            </div>

            <div className="calendar-grid">
              {plan.daily_plan.map((day) => (
                <div
                  key={day.day}
                  className={`calendar-day ${
                    completedDays.has(day.day) ? "completed" : ""
                  }`}
                  onClick={() =>
                    setExpandedDay(expandedDay === day.day ? null : day.day)
                  }
                >
                  <div className="day-number">Day {day.day}</div>
                  <div
                    className="difficulty-dot"
                    style={{
                      backgroundColor: getDifficultyColor(day.difficulty_level),
                    }}
                    title={day.difficulty_level}
                  />
                  <p className="focus">{day.focus_area}</p>

                  {expandedDay === day.day && (
                    <div className="day-details">
                      <h4>{day.action}</h4>
                      {day.carbon_saved_vs_typical_kg && (
                        <p className="savings">
                          Saves ~{day.carbon_saved_vs_typical_kg} kg CO₂
                        </p>
                      )}
                      <button
                        className={`complete-btn ${
                          completedDays.has(day.day) ? "completed" : ""
                        }`}
                        onClick={(e) => {
                          e.stopPropagation();
                          toggleDayCompletion(day.day);
                        }}
                      >
                        {completedDays.has(day.day)
                          ? "✅ Completed"
                          : "Mark Complete"}
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* RECIPES TAB */}
        {activeTab === "recipes" && (
          <div className="recipes-section">
            <h3>🍱 Low-Carbon Recipe Suggestions</h3>
            <div className="recipes-grid">
              {plan.recipes.map((recipe, idx) => (
                <div key={idx} className="recipe-card">
                  <h4>{recipe.name}</h4>
                  <div className="recipe-stats">
                    <div className="stat">
                      <label>Carbon Footprint</label>
                      <p>{recipe.carbon_footprint_kg} kg CO₂</p>
                    </div>
                    <div className="stat">
                      <label>Protein</label>
                      <p>{recipe.protein_g}g</p>
                    </div>
                    <div className="stat">
                      <label>Prep Time</label>
                      <p>{recipe.prep_time_minutes} min</p>
                    </div>
                  </div>
                  <div className="savings">
                    💚 Saves {recipe.savings_vs_typical_kg} kg vs typical meal
                  </div>
                  <p className="ingredients">
                    <strong>Ingredients:</strong>{" "}
                    {recipe.ingredients.join(", ")}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* COMMUTE TAB */}
        {activeTab === "commute" && (
          <div className="commute-section">
            <h3>🚗 Commute Alternatives</h3>
            <div className="commute-options">
              {plan.commute_alternatives.map((option, idx) => (
                <div key={idx} className="commute-option">
                  <h4>{option.mode}</h4>
                  <div className="option-grid">
                    <div className="metric">
                      <label>Annual Carbon</label>
                      <p className="value">
                        {option.annual_carbon_kg.toFixed(0)} kg CO₂
                      </p>
                    </div>
                    <div className="metric">
                      <label>Monthly Cost</label>
                      <p className="value">
                        ${option.cost_per_month.toFixed(0)}
                      </p>
                    </div>
                    <div className="metric">
                      <label>Time/Day</label>
                      <p className="value">{option.time_per_day_minutes} min</p>
                    </div>
                    <div className="metric">
                      <label>Feasibility</label>
                      <p className="value">
                        {(option.feasibility_score * 10).toFixed(0)}%
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* HABITS TAB */}
        {activeTab === "habits" && (
          <div className="habits-section">
            <div className="habit-changes">
              <h3>🔄 Recommended Habit Changes</h3>
              <ul className="habit-list">
                {plan.habit_changes.map((change, idx) => (
                  <li key={idx} className="habit-item">
                    {change}
                  </li>
                ))}
              </ul>
            </div>

            <div className="subscriptions">
              <h3>📦 Subscriptions & Recurring Purchases to Replace</h3>
              <div className="subscriptions-grid">
                {plan.subscriptions_to_replace.map((sub, idx) => (
                  <div key={idx} className="subscription-card">
                    <h4>{sub.item_name}</h4>
                    <p className="frequency">{sub.frequency}</p>
                    <div className="sub-metrics">
                      <div className="metric">
                        <label>Annual Impact</label>
                        <p className="value">
                          {sub.annual_carbon_kg.toFixed(1)} kg CO₂
                        </p>
                      </div>
                      <div className="metric">
                        <label>Potential Savings</label>
                        <p className="value savings">
                          {sub.potential_savings_kg.toFixed(1)} kg
                        </p>
                      </div>
                    </div>
                    <div className="alternative">
                      <strong>Try:</strong> {sub.alternative}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ThirtyDayPlanView;
