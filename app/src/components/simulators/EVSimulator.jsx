import { useState } from "react";
import { api } from "../../lib/api";
import SimulatorCard, { SimInput, SimButton, SimResult } from "./SimulatorCard";

export default function EVSimulator() {
  const [annualKm, setAnnualKm] = useState(15000);
  const [fuelEfficiency, setFuelEfficiency] = useState(10);
  const [evEfficiency, setEvEfficiency] = useState(0.2);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const simulate = async () => {
    setLoading(true);
    try {
      const res = await api.post("/simulate_electric_vehicle", {
        annual_km: annualKm, current_fuel_efficiency: fuelEfficiency, ev_efficiency: evEfficiency,
      });
      setResult(res);
    } catch { /* ignore */ } finally { setLoading(false); }
  };

  return (
    <SimulatorCard title="Switch to Electric Vehicle" icon="🚗">
      <SimInput label="Annual km driven" type="number" min="1000" value={annualKm} onChange={(e) => setAnnualKm(parseInt(e.target.value))} />
      <SimInput label="Fuel efficiency (L/100km)" type="number" min="5" step="0.1" value={fuelEfficiency} onChange={(e) => setFuelEfficiency(parseFloat(e.target.value))} />
      <SimInput label="EV efficiency (kWh/km)" type="number" min="0.1" step="0.1" value={evEfficiency} onChange={(e) => setEvEfficiency(parseFloat(e.target.value))} />
      <SimButton onClick={simulate} loading={loading}>Simulate</SimButton>
      {result && (
        <SimResult>
          <h4 className="font-semibold text-green-400 text-sm">{result.scenario}</h4>
          <div className="mt-2 space-y-1 text-sm">
            <p className="text-gray-300">CO₂ savings: <span className="text-white font-medium">{result.annual_co2_savings} kg</span></p>
            <p className="text-gray-300">Current: <span className="text-white font-medium">{result.current_annual_co2} kg</span> → New: <span className="text-white font-medium">{result.new_annual_co2} kg</span></p>
          </div>
        </SimResult>
      )}
    </SimulatorCard>
  );
}
