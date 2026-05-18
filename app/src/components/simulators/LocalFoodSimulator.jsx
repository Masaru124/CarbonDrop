import { useState } from "react";
import { api } from "../../lib/api";
import SimulatorCard, { SimInput, SimButton, SimResult } from "./SimulatorCard";

export default function LocalFoodSimulator() {
  const [importedMeals, setImportedMeals] = useState(10);
  const [localReductionPercent, setLocalReductionPercent] = useState(50);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const simulate = async () => {
    setLoading(true);
    try {
      const res = await api.post("/simulate_local_food", {
        imported_meals_per_week: importedMeals, local_reduction_percent: localReductionPercent, weeks: 52,
      });
      setResult(res);
    } catch { /* ignore */ } finally { setLoading(false); }
  };

  return (
    <SimulatorCard title="Choose Local Food" icon="🌽">
      <SimInput label="Imported meals per week" type="number" min="1" value={importedMeals} onChange={(e) => setImportedMeals(parseInt(e.target.value))} />
      <SimInput label="Switch to local (%)" type="number" min="10" max="100" value={localReductionPercent} onChange={(e) => setLocalReductionPercent(parseInt(e.target.value))} />
      <SimButton onClick={simulate} loading={loading}>Simulate</SimButton>
      {result && (
        <SimResult>
          <h4 className="font-semibold text-green-400 text-sm">{result.scenario}</h4>
          <div className="mt-2 space-y-1 text-sm">
            <p className="text-gray-300">Weekly CO₂ savings: <span className="text-white font-medium">{result.weekly_co2_savings} kg</span></p>
            <p className="text-gray-300">Annual CO₂ savings: <span className="text-white font-medium">{result.annual_co2_savings} kg</span></p>
          </div>
        </SimResult>
      )}
    </SimulatorCard>
  );
}
