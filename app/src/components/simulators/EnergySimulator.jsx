import { useState } from "react";
import { api } from "../../lib/api";
import SimulatorCard, { SimInput, SimButton, SimResult } from "./SimulatorCard";

export default function EnergySimulator() {
  const [currentBulbs, setCurrentBulbs] = useState(10);
  const [ledBulbs, setLedBulbs] = useState(10);
  const [hoursPerDay, setHoursPerDay] = useState(4);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const simulate = async () => {
    setLoading(true);
    try {
      const res = await api.post("/simulate_energy_efficiency", {
        current_bulbs: currentBulbs, led_bulbs: ledBulbs, hours_per_day: hoursPerDay, days_per_year: 365,
      });
      setResult(res);
    } catch { /* ignore */ } finally { setLoading(false); }
  };

  return (
    <SimulatorCard title="Switch to LED Bulbs" icon="💡">
      <SimInput label="Current incandescent bulbs" type="number" min="1" value={currentBulbs} onChange={(e) => setCurrentBulbs(parseInt(e.target.value))} />
      <SimInput label="LED replacement bulbs" type="number" min="1" value={ledBulbs} onChange={(e) => setLedBulbs(parseInt(e.target.value))} />
      <SimInput label="Hours per day" type="number" min="1" max="24" value={hoursPerDay} onChange={(e) => setHoursPerDay(parseInt(e.target.value))} />
      <SimButton onClick={simulate} loading={loading}>Simulate</SimButton>
      {result && (
        <SimResult>
          <h4 className="font-semibold text-green-400 text-sm">{result.scenario}</h4>
          <div className="mt-2 space-y-1 text-sm">
            <p className="text-gray-300">Annual energy savings: <span className="text-white font-medium">{result.annual_energy_savings} kWh</span></p>
            <p className="text-gray-300">CO₂ savings: <span className="text-white font-medium">{result.annual_co2_savings} kg</span></p>
          </div>
        </SimResult>
      )}
    </SimulatorCard>
  );
}
