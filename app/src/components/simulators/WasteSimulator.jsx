import { useState } from "react";
import { api } from "../../lib/api";
import SimulatorCard, { SimInput, SimButton, SimResult } from "./SimulatorCard";

export default function WasteSimulator() {
  const [wasteKgPerWeek, setWasteKgPerWeek] = useState(5);
  const [wasteReductionPercent, setWasteReductionPercent] = useState(30);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const simulate = async () => {
    setLoading(true);
    try {
      const res = await api.post("/simulate_waste_reduction", {
        current_waste_kg_per_week: wasteKgPerWeek, reduction_percent: wasteReductionPercent, weeks: 52,
      });
      setResult(res);
    } catch { /* ignore */ } finally { setLoading(false); }
  };

  return (
    <SimulatorCard title="Reduce Food Waste" icon="🗑️">
      <SimInput label="Current food waste (kg/week)" type="number" min="1" step="0.5" value={wasteKgPerWeek} onChange={(e) => setWasteKgPerWeek(parseFloat(e.target.value))} />
      <SimInput label="Waste reduction (%)" type="number" min="10" max="80" value={wasteReductionPercent} onChange={(e) => setWasteReductionPercent(parseInt(e.target.value))} />
      <SimButton onClick={simulate} loading={loading}>Simulate</SimButton>
      {result && (
        <SimResult>
          <h4 className="font-semibold text-green-400 text-sm">{result.scenario}</h4>
          <div className="mt-2 space-y-1 text-sm">
            <p className="text-gray-300">Annual waste reduction: <span className="text-white font-medium">{result.annual_waste_reduction} kg</span></p>
            <p className="text-gray-300">CO₂ savings: <span className="text-white font-medium">{result.annual_co2_savings} kg</span></p>
          </div>
        </SimResult>
      )}
    </SimulatorCard>
  );
}
