/**
 * Simulation Tool Component
 * Allows users to simulate lifestyle changes and see carbon impact
 */

import React, { useState } from "react";
import { useSimulation } from "../hooks/useCarbonBudgeting";
import "./SimulationTool.css";

export function SimulationTool() {
  const [changeType, setChangeType] = useState("diet");
  const [parameters, setParameters] = useState({});
  const [results, setResults] = useState(null);
  const { simulate, loading, error } = useSimulation();

  const handleSimulate = async () => {
    // Ensure defaults for missing parameters to avoid backend errors
    const payload = { ...parameters };
    if (changeType === "diet") {
      if (payload.reduction_percent === undefined)
        payload.reduction_percent = 30;
      if (!payload.removed_items) payload.removed_items = [];
    } else if (changeType === "commute") {
      if (!payload.from_mode) payload.from_mode = "car";
      if (!payload.to_mode) payload.to_mode = "bike";
      if (payload.days_per_week === undefined) payload.days_per_week = 5;
    } else if (changeType === "shopping") {
      if (payload.reduction_percent === undefined)
        payload.reduction_percent = 30;
    } else if (changeType === "energy") {
      if (payload.efficiency_improvement_percent === undefined)
        payload.efficiency_improvement_percent = 20;
    }

    const result = await simulate(changeType, payload);
    if (result) {
      setResults(result);
    }
  };

  const updateParameter = (key, value) => {
    setParameters({ ...parameters, [key]: value });
  };

  const renderParameterInputs = () => {
    switch (changeType) {
      case "diet":
        return (
          <div className="parameter-inputs">
            <label>
              Reduction Percentage:
              <input
                type="range"
                min="0"
                max="100"
                step="5"
                value={parameters.reduction_percent || 30}
                onChange={(e) =>
                  updateParameter("reduction_percent", parseInt(e.target.value))
                }
              />
              <span>{parameters.reduction_percent || 30}%</span>
            </label>
            <p className="parameter-help">
              How much less meat and animal products will you consume?
            </p>
          </div>
        );
      case "commute":
        return (
          <div className="parameter-inputs">
            <label>
              From Mode:
              <select
                value={parameters.from_mode || "car"}
                onChange={(e) => updateParameter("from_mode", e.target.value)}
              >
                <option value="car">🚗 Car</option>
                <option value="public_transit">🚌 Public Transit</option>
                <option value="carpool">👥 Carpool</option>
                <option value="bike">🚴 Bike</option>
              </select>
            </label>
            <label>
              To Mode:
              <select
                value={parameters.to_mode || "bike"}
                onChange={(e) => updateParameter("to_mode", e.target.value)}
              >
                <option value="car">🚗 Car</option>
                <option value="public_transit">🚌 Public Transit</option>
                <option value="carpool">👥 Carpool</option>
                <option value="bike">🚴 Bike</option>
                <option value="walk">🚶 Walk</option>
              </select>
            </label>
            <label>
              Days Per Week:
              <input
                type="range"
                min="1"
                max="7"
                value={parameters.days_per_week || 5}
                onChange={(e) =>
                  updateParameter("days_per_week", parseInt(e.target.value))
                }
              />
              <span>{parameters.days_per_week || 5} days</span>
            </label>
          </div>
        );
      case "shopping":
        return (
          <div className="parameter-inputs">
            <label>
              Purchase Reduction:
              <input
                type="range"
                min="0"
                max="100"
                step="5"
                value={parameters.reduction_percent || 30}
                onChange={(e) =>
                  updateParameter("reduction_percent", parseInt(e.target.value))
                }
              />
              <span>{parameters.reduction_percent || 30}%</span>
            </label>
            <p className="parameter-help">
              Switch to secondhand/sustainable alternatives
            </p>
          </div>
        );
      case "energy":
        return (
          <div className="parameter-inputs">
            <label>
              Energy Efficiency Improvement:
              <input
                type="range"
                min="0"
                max="50"
                step="5"
                value={parameters.efficiency_improvement_percent || 20}
                onChange={(e) =>
                  updateParameter(
                    "efficiency_improvement_percent",
                    parseInt(e.target.value)
                  )
                }
              />
              <span>{parameters.efficiency_improvement_percent || 20}%</span>
            </label>
            <p className="parameter-help">
              e.g., LED bulbs, better insulation, smart thermostat
            </p>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="simulation-tool">
      <h2>🔄 What-If Simulator</h2>
      <p className="description">
        Explore how lifestyle changes impact your carbon footprint
      </p>

      <div className="simulator-container">
        <div className="left-panel">
          <h3>Choose a Change</h3>
          <div className="change-options">
            {[
              {
                value: "diet",
                label: "🍽️ Diet",
                description: "Reduce meat consumption",
              },
              {
                value: "commute",
                label: "🚗 Commute",
                description: "Change transportation",
              },
              {
                value: "shopping",
                label: "🛍️ Shopping",
                description: "Reduce consumption",
              },
              {
                value: "energy",
                label: "⚡ Energy",
                description: "Home efficiency",
              },
            ].map((option) => (
              <button
                key={option.value}
                className={`option-button ${
                  changeType === option.value ? "active" : ""
                }`}
                onClick={() => {
                  setChangeType(option.value);
                  setResults(null);
                }}
              >
                <span className="option-label">{option.label}</span>
                <span className="option-desc">{option.description}</span>
              </button>
            ))}
          </div>
        </div>

        <div className="right-panel">
          <h3>Configure Change</h3>
          {renderParameterInputs()}

          <button
            className="simulate-button"
            onClick={handleSimulate}
            disabled={loading}
          >
            {loading ? "Calculating..." : "Calculate Impact"}
          </button>

          {error && <div className="error-message">Error: {error}</div>}

          {results && (
            <div className="results-section">
              <h3>📊 Impact Summary</h3>
              <div className="impact-cards">
                <div className="impact-card">
                  <label>Daily Reduction</label>
                  <p className="value">
                    {results.estimated_reduction_kg} kg CO₂
                  </p>
                  <p className="percent">
                    (-{results.estimated_reduction_percent}%)
                  </p>
                </div>
                <div className="impact-card">
                  <label>Annual Impact</label>
                  <p className="value">{results.annual_impact_kg} kg CO₂</p>
                  <p className="percent">per year</p>
                </div>
                <div className="impact-card">
                  <label>Equivalent To</label>
                  <p className="value">
                    {Math.round(results.annual_impact_kg / 21)} 🌳
                  </p>
                  <p className="percent">trees</p>
                </div>
              </div>

              <div className="change-details">
                <h4>{results.change_description}</h4>
                <p className="affected-categories">
                  Affects: {results.affected_categories.join(", ")}
                </p>
              </div>

              <div className="comparison">
                <h4>How It Compares</h4>
                <ul>
                  <li>
                    ✈️ Equivalent to{" "}
                    {(results.annual_impact_kg / 100).toFixed(1)} fewer
                    transatlantic flights
                  </li>
                  <li>
                    🚗 Like driving{" "}
                    {(results.annual_impact_kg / 0.2).toFixed(0)} fewer km in a
                    car
                  </li>
                  <li>
                    💡 Energy to power your home for{" "}
                    {(results.annual_impact_kg / 1).toFixed(0)} days
                  </li>
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default SimulationTool;
