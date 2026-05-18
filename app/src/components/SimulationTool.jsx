import { useState } from "react";
import Card from "../ui/Card";
import Button from "../ui/Button";
import Spinner from "../ui/Spinner";

const changeOptions = [
  { value: "diet", label: "🍽️ Diet", description: "Reduce meat consumption" },
  { value: "commute", label: "🚗 Commute", description: "Change transportation" },
  { value: "shopping", label: "🛍️ Shopping", description: "Reduce consumption" },
  { value: "energy", label: "⚡ Energy", description: "Home efficiency" },
];

export function SimulationTool({ onSimulate, result, loading, error }) {
  const [changeType, setChangeType] = useState("diet");
  const [parameters, setParameters] = useState({});

  const updateParameter = (key, value) => {
    setParameters((prev) => ({ ...prev, [key]: value }));
  };

  const handleSimulate = () => {
    const payload = { ...parameters };
    if (changeType === "diet") {
      if (payload.reduction_percent === undefined) payload.reduction_percent = 30;
      if (!payload.removed_items) payload.removed_items = [];
    } else if (changeType === "commute") {
      if (!payload.from_mode) payload.from_mode = "car";
      if (!payload.to_mode) payload.to_mode = "bike";
      if (payload.days_per_week === undefined) payload.days_per_week = 5;
    } else if (changeType === "shopping") {
      if (payload.reduction_percent === undefined) payload.reduction_percent = 30;
    } else if (changeType === "energy") {
      if (payload.efficiency_improvement_percent === undefined) payload.efficiency_improvement_percent = 20;
    }
    onSimulate(changeType, payload);
  };

  const renderParams = () => {
    switch (changeType) {
      case "diet":
        return (
          <div className="space-y-4">
            <div>
              <label className="text-sm text-gray-300 block mb-2">Reduction Percentage</label>
              <input
                type="range"
                min="0" max="100" step="5"
                value={parameters.reduction_percent || 30}
                onChange={(e) => updateParameter("reduction_percent", parseInt(e.target.value))}
                className="w-full accent-green-500"
              />
              <span className="text-sm font-semibold text-green-400">{parameters.reduction_percent || 30}%</span>
              <p className="text-xs text-gray-500 mt-1">How much less meat and animal products will you consume?</p>
            </div>
          </div>
        );
      case "commute":
        return (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-sm text-gray-300 block mb-1">From</label>
                <select
                  value={parameters.from_mode || "car"}
                  onChange={(e) => updateParameter("from_mode", e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white text-sm"
                >
                  <option value="car">🚗 Car</option>
                  <option value="public_transit">🚌 Public Transit</option>
                  <option value="carpool">👥 Carpool</option>
                  <option value="bike">🚴 Bike</option>
                </select>
              </div>
              <div>
                <label className="text-sm text-gray-300 block mb-1">To</label>
                <select
                  value={parameters.to_mode || "bike"}
                  onChange={(e) => updateParameter("to_mode", e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white text-sm"
                >
                  <option value="car">🚗 Car</option>
                  <option value="public_transit">🚌 Public Transit</option>
                  <option value="carpool">👥 Carpool</option>
                  <option value="bike">🚴 Bike</option>
                  <option value="walk">🚶 Walk</option>
                </select>
              </div>
            </div>
            <div>
              <label className="text-sm text-gray-300 block mb-2">Days Per Week: {parameters.days_per_week || 5}</label>
              <input
                type="range" min="1" max="7"
                value={parameters.days_per_week || 5}
                onChange={(e) => updateParameter("days_per_week", parseInt(e.target.value))}
                className="w-full accent-green-500"
              />
            </div>
          </div>
        );
      case "shopping":
        return (
          <div className="space-y-4">
            <div>
              <label className="text-sm text-gray-300 block mb-2">Purchase Reduction</label>
              <input
                type="range" min="0" max="100" step="5"
                value={parameters.reduction_percent || 30}
                onChange={(e) => updateParameter("reduction_percent", parseInt(e.target.value))}
                className="w-full accent-green-500"
              />
              <span className="text-sm font-semibold text-green-400">{parameters.reduction_percent || 30}%</span>
              <p className="text-xs text-gray-500 mt-1">Switch to secondhand/sustainable alternatives</p>
            </div>
          </div>
        );
      case "energy":
        return (
          <div className="space-y-4">
            <div>
              <label className="text-sm text-gray-300 block mb-2">Energy Efficiency Improvement</label>
              <input
                type="range" min="0" max="50" step="5"
                value={parameters.efficiency_improvement_percent || 20}
                onChange={(e) => updateParameter("efficiency_improvement_percent", parseInt(e.target.value))}
                className="w-full accent-green-500"
              />
              <span className="text-sm font-semibold text-green-400">{parameters.efficiency_improvement_percent || 20}%</span>
              <p className="text-xs text-gray-500 mt-1">e.g., LED bulbs, better insulation, smart thermostat</p>
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="grid md:grid-cols-2 gap-6">
      <Card>
        <h3 className="font-semibold mb-4">Choose a Change</h3>
        <div className="space-y-2">
          {changeOptions.map((option) => (
            <button
              key={option.value}
              onClick={() => { setChangeType(option.value); setParameters({}); }}
              className={`w-full text-left px-4 py-3 rounded-lg border transition ${
                changeType === option.value
                  ? "border-green-500 bg-green-500/10 text-green-400"
                  : "border-gray-700 bg-transparent text-gray-300 hover:border-gray-500"
              }`}
            >
              <span className="block font-medium">{option.label}</span>
              <span className="text-xs opacity-70">{option.description}</span>
            </button>
          ))}
        </div>
      </Card>

      <Card>
        <h3 className="font-semibold mb-4">Configure Change</h3>
        {renderParams()}

        <Button onClick={handleSimulate} disabled={loading} loading={loading} className="w-full mt-6">
          {loading ? "Calculating..." : "Calculate Impact"}
        </Button>

        {error && (
          <div className="mt-4 p-3 bg-red-900/30 border border-red-700 rounded-lg text-sm text-red-400">
            Error: {error}
          </div>
        )}

        {result && (
          <div className="mt-6 space-y-4 animate-fade-in">
            <h4 className="font-semibold text-green-400">📊 Impact Summary</h4>
            <div className="grid grid-cols-3 gap-3">
              {[
                { label: "Daily Reduction", value: `${result.estimated_reduction_kg} kg`, sub: `(-${result.estimated_reduction_percent}%)` },
                { label: "Annual Impact", value: `${result.annual_impact_kg} kg`, sub: "per year" },
                { label: "Equivalent To", value: `${Math.round(result.annual_impact_kg / 21)} 🌳`, sub: "trees" },
              ].map((item) => (
                <div key={item.label} className="bg-gray-800/50 rounded-lg p-3 text-center">
                  <p className="text-xs text-gray-400 mb-1">{item.label}</p>
                  <p className="text-lg font-bold text-white">{item.value}</p>
                  <p className="text-xs text-gray-500">{item.sub}</p>
                </div>
              ))}
            </div>

            {result.change_description && (
              <p className="text-sm text-gray-300">{result.change_description}</p>
            )}

            {result.affected_categories && (
              <p className="text-xs text-gray-500">Affects: {result.affected_categories.join(", ")}</p>
            )}

            <div className="bg-gray-800/50 rounded-lg p-4 text-sm text-gray-400 space-y-1">
              <p>✈️ Equivalent to {(result.annual_impact_kg / 100).toFixed(1)} fewer transatlantic flights</p>
              <p>🚗 Like driving {(result.annual_impact_kg / 0.2).toFixed(0)} fewer km in a car</p>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}

export default SimulationTool;
