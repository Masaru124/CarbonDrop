import { useState } from "react";
import { api } from "../../lib/api";
import SimulatorCard, { SimInput, SimButton, SimResult } from "./SimulatorCard";

export default function TransportSimulator() {
  const [trips, setTrips] = useState(4);
  const [distance, setDistance] = useState(500);
  const [fromMode, setFromMode] = useState("flight");
  const [toMode, setToMode] = useState("train");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const simulate = async () => {
    setLoading(true);
    try {
      const res = await api.post("/simulate_transport_switch", {
        trips_per_year: trips, distance_per_trip_km: distance, from_mode: fromMode, to_mode: toMode,
      });
      setResult(res);
    } catch { /* ignore */ } finally { setLoading(false); }
  };

  return (
    <SimulatorCard title="Switch Transport Mode" icon="🚗">
      <SimInput label="Trips per year" type="number" min="1" value={trips} onChange={(e) => setTrips(parseInt(e.target.value))} />
      <SimInput label="Distance per trip (km)" type="number" min="1" value={distance} onChange={(e) => setDistance(parseFloat(e.target.value))} />
      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className="block text-xs text-gray-400 mb-1.5 uppercase tracking-wider">From</label>
          <select value={fromMode} onChange={(e) => setFromMode(e.target.value)} className="w-full px-3 py-2 rounded-lg bg-gray-800/80 text-white border border-gray-700 focus:border-green-500 focus:outline-none focus:ring-1 focus:ring-green-500/50 transition text-sm">
            <option value="flight">Flight</option>
            <option value="train">Train</option>
            <option value="bus">Bus</option>
            <option value="car">Car</option>
          </select>
        </div>
        <div>
          <label className="block text-xs text-gray-400 mb-1.5 uppercase tracking-wider">To</label>
          <select value={toMode} onChange={(e) => setToMode(e.target.value)} className="w-full px-3 py-2 rounded-lg bg-gray-800/80 text-white border border-gray-700 focus:border-green-500 focus:outline-none focus:ring-1 focus:ring-green-500/50 transition text-sm">
            <option value="flight">Flight</option>
            <option value="train">Train</option>
            <option value="bus">Bus</option>
            <option value="car">Car</option>
          </select>
        </div>
      </div>
      <SimButton onClick={simulate} loading={loading}>Simulate</SimButton>
      {result && (
        <SimResult>
          <h4 className="font-semibold text-green-400 text-sm">{result.scenario}</h4>
          <div className="mt-2 space-y-1 text-sm">
            <p className="text-gray-300">Annual CO₂ savings: <span className="text-white font-medium">{result.annual_savings} kg</span></p>
            <p className="text-gray-300">Original: <span className="text-white font-medium">{result.original_annual_co2} kg</span> → New: <span className="text-white font-medium">{result.new_annual_co2} kg</span></p>
          </div>
        </SimResult>
      )}
    </SimulatorCard>
  );
}
