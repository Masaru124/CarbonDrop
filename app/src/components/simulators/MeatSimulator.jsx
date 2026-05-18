import { useState } from "react";
import { api } from "../../lib/api";
import SimulatorCard, { SimInput, SimButton, SimResult } from "./SimulatorCard";

export default function MeatSimulator() {
  const [meatMeals, setMeatMeals] = useState(3);
  const [weeks, setWeeks] = useState(52);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const simulate = async () => {
    setLoading(true);
    try {
      const res = await api.post("/simulate_meat_replacement", { meat_meals_per_week: meatMeals, weeks });
      setResult(res);
    } catch { /* ignore */ } finally { setLoading(false); }
  };

  return (
    <SimulatorCard title="Replace Meat Meals" icon="🥩">
      <SimInput label="Meat meals per week" type="number" min="1" max="21" value={meatMeals} onChange={(e) => setMeatMeals(parseInt(e.target.value))} />
      <SimInput label="Weeks per year" type="number" min="1" max="52" value={weeks} onChange={(e) => setWeeks(parseInt(e.target.value))} />
      <SimButton onClick={simulate} loading={loading}>Simulate</SimButton>
      {result && (
        <SimResult>
          <h4 className="font-semibold text-green-400 text-sm">{result.scenario}</h4>
          <div className="mt-2 space-y-1 text-sm">
            <p className="text-gray-300">Weekly CO₂ savings: <span className="text-white font-medium">{result.weekly_savings} kg</span></p>
            <p className="text-gray-300">Annual CO₂ savings: <span className="text-white font-medium">{result.annual_savings} kg</span></p>
          </div>
        </SimResult>
      )}
    </SimulatorCard>
  );
}
