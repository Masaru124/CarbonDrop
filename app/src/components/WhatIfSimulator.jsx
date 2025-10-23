import { useState, useEffect } from "react";

export default function WhatIfSimulator() {
  const [meatMeals, setMeatMeals] = useState(3);
  const [weeks, setWeeks] = useState(52);
  const [meatResult, setMeatResult] = useState(null);
  const [trips, setTrips] = useState(4);
  const [distance, setDistance] = useState(500);
  const [fromMode, setFromMode] = useState("flight");
  const [toMode, setToMode] = useState("train");
  const [transportResult, setTransportResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // New simulation state variables
  const [currentBulbs, setCurrentBulbs] = useState(10);
  const [ledBulbs, setLedBulbs] = useState(10);
  const [hoursPerDay, setHoursPerDay] = useState(4);
  const [energyResult, setEnergyResult] = useState(null);

  const [annualKm, setAnnualKm] = useState(15000);
  const [fuelEfficiency, setFuelEfficiency] = useState(10);
  const [evEfficiency, setEvEfficiency] = useState(0.2);
  const [evResult, setEvResult] = useState(null);

  const [importedMeals, setImportedMeals] = useState(10);
  const [localReductionPercent, setLocalReductionPercent] = useState(50);
  const [localFoodResult, setLocalFoodResult] = useState(null);

  const [wasteKgPerWeek, setWasteKgPerWeek] = useState(5);
  const [wasteReductionPercent, setWasteReductionPercent] = useState(30);
  const [wasteResult, setWasteResult] = useState(null);

  // Offset related state
  const [offsetResult, setOffsetResult] = useState(null);
  const [userOffsets, setUserOffsets] = useState(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userCredits, setUserCredits] = useState(0);

  const simulateMeatReplacement = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        "http://localhost:8000/simulate_meat_replacement",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ meat_meals_per_week: meatMeals, weeks }),
        }
      );
      const result = await response.json();
      setMeatResult(result);
    } catch (error) {
      console.error("Error simulating meat replacement:", error);
    }
    setLoading(false);
  };

  const simulateTransportSwitch = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        "http://localhost:8000/simulate_transport_switch",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            trips_per_year: trips,
            distance_per_trip_km: distance,
            from_mode: fromMode,
            to_mode: toMode,
          }),
        }
      );
      const result = await response.json();
      setTransportResult(result);
    } catch (error) {
      console.error("Error simulating transport switch:", error);
    }
    setLoading(false);
  };

  const simulateEnergyEfficiency = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        "http://localhost:8000/simulate_energy_efficiency",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            current_bulbs: currentBulbs,
            led_bulbs: ledBulbs,
            hours_per_day: hoursPerDay,
            days_per_year: 365,
          }),
        }
      );
      const result = await response.json();
      setEnergyResult(result);
    } catch (error) {
      console.error("Error simulating energy efficiency:", error);
    }
    setLoading(false);
  };

  const simulateElectricVehicle = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        "http://localhost:8000/simulate_electric_vehicle",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            annual_km: annualKm,
            current_fuel_efficiency: fuelEfficiency,
            ev_efficiency: evEfficiency,
          }),
        }
      );
      const result = await response.json();
      setEvResult(result);
    } catch (error) {
      console.error("Error simulating electric vehicle:", error);
    }
    setLoading(false);
  };

  const simulateLocalFood = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        "http://localhost:8000/simulate_local_food",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            imported_meals_per_week: importedMeals,
            local_reduction_percent: localReductionPercent,
            weeks: 52,
          }),
        }
      );
      const result = await response.json();
      setLocalFoodResult(result);
    } catch (error) {
      console.error("Error simulating local food:", error);
    }
    setLoading(false);
  };

  const simulateWasteReduction = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        "http://localhost:8000/simulate_waste_reduction",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            current_waste_kg_per_week: wasteKgPerWeek,
            reduction_percent: wasteReductionPercent,
            weeks: 52,
          }),
        }
      );
      const result = await response.json();
      setWasteResult(result);
    } catch (error) {
      console.error("Error simulating waste reduction:", error);
    }
    setLoading(false);
  };

  const plantTrees = async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      alert("Please login to plant trees");
      return;
    }

    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/plant_trees", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });
      if (!response.ok) {
        const errorData = await response.json();
        alert(`Error planting trees: ${errorData.detail || "Unknown error"}`);
        setLoading(false);
        return;
      }
      const result = await response.json();
      setOffsetResult(result);
      fetchUserOffsets();
      fetchUserCredits();
    } catch (error) {
      console.error("Error planting trees:", error);
    }
    setLoading(false);
  };

  const fetchUserOffsets = async () => {
    const token = localStorage.getItem("token");
    if (!token) return;

    try {
      const response = await fetch("http://localhost:8000/user_offsets", {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await response.json();
      setUserOffsets(data);
    } catch (error) {
      console.error("Error fetching user offsets:", error);
    }
  };

  const fetchUserCredits = async () => {
    const token = localStorage.getItem("token");
    if (!token) return;

    try {
      const response = await fetch("http://localhost:8000/auth/me", {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await response.json();
      setUserCredits(data.eco_credits || 0);
    } catch (error) {
      console.error("Error fetching user credits:", error);
    }
  };

  useEffect(() => {
    const token = localStorage.getItem("token");
    setIsLoggedIn(!!token);
    if (token) {
      fetchUserOffsets();
      fetchUserCredits();
    }
  }, []);

  return (
    <div className="p-6 bg-[#121212] text-white rounded-xl shadow-md">
      <h2 className="text-2xl font-bold mb-6 text-green-400">What-if Simulator</h2>

      <div className="grid md:grid-cols-2 gap-8">
        {/* Meat Replacement */}
        <div className="border border-gray-700 bg-gray-900 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-4 text-green-300">
            Replace Meat Meals with Plant-Based
          </h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-300 mb-1">Meat meals per week:</label>
              <input
                type="number"
                value={meatMeals}
                onChange={(e) => setMeatMeals(parseInt(e.target.value))}
                className="w-full p-2 rounded bg-gray-800 text-white border border-gray-700"
                min="1"
                max="21"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-300 mb-1">Weeks per year:</label>
              <input
                type="number"
                value={weeks}
                onChange={(e) => setWeeks(parseInt(e.target.value))}
                className="w-full p-2 rounded bg-gray-800 text-white border border-gray-700"
                min="1"
                max="52"
              />
            </div>
            <button
              onClick={simulateMeatReplacement}
              disabled={loading}
              className="w-full bg-green-600 text-white py-2 px-4 rounded hover:bg-green-700 disabled:opacity-50"
            >
              {loading ? "Calculating..." : "Simulate"}
            </button>
          </div>

          {meatResult && (
            <div className="mt-4 p-3 bg-green-900/40 border border-green-700 rounded">
              <h4 className="font-semibold text-green-400">{meatResult.scenario}</h4>
              <p className="text-sm text-gray-300 mt-2">
                Weekly CO₂ savings: <strong>{meatResult.weekly_savings} kg</strong>
                <br />
                Annual CO₂ savings: <strong>{meatResult.annual_savings} kg</strong>
              </p>
            </div>
          )}
        </div>

        {/* Transport Switch */}
        <div className="border border-gray-700 bg-gray-900 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-4 text-blue-300">Switch Transport Mode</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-300 mb-1">Trips per year:</label>
              <input
                type="number"
                value={trips}
                onChange={(e) => setTrips(parseInt(e.target.value))}
                className="w-full p-2 rounded bg-gray-800 text-white border border-gray-700"
                min="1"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-300 mb-1">Distance per trip (km):</label>
              <input
                type="number"
                value={distance}
                onChange={(e) => setDistance(parseFloat(e.target.value))}
                className="w-full p-2 rounded bg-gray-800 text-white border border-gray-700"
                min="1"
              />
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-sm text-gray-300 mb-1">From:</label>
                <select
                  value={fromMode}
                  onChange={(e) => setFromMode(e.target.value)}
                  className="w-full p-2 rounded bg-gray-800 text-white border border-gray-700"
                >
                  <option value="flight">Flight</option>
                  <option value="train">Train</option>
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-300 mb-1">To:</label>
                <select
                  value={toMode}
                  onChange={(e) => setToMode(e.target.value)}
                  className="w-full p-2 rounded bg-gray-800 text-white border border-gray-700"
                >
                  <option value="flight">Flight</option>
                  <option value="train">Train</option>
                </select>
              </div>
            </div>
            <button
              onClick={simulateTransportSwitch}
              disabled={loading}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? "Calculating..." : "Simulate"}
            </button>
          </div>

          {transportResult && (
            <div className="mt-4 p-3 bg-blue-900/40 border border-blue-700 rounded">
              <h4 className="font-semibold text-blue-400">{transportResult.scenario}</h4>
              <p className="text-sm text-gray-300 mt-2">
                Annual CO₂ savings: <strong>{transportResult.annual_savings} kg</strong>
                <br />
                Original annual CO₂: <strong>{transportResult.original_annual_co2} kg</strong>
                <br />
                New annual CO₂: <strong>{transportResult.new_annual_co2} kg</strong>
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Additional Simulations */}
      <div className="grid md:grid-cols-2 gap-8 mt-8">
        {/* Energy Efficiency */}
        <div className="border border-gray-700 bg-gray-900 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-4 text-yellow-300">Switch to LED Bulbs</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-300 mb-1">Current incandescent bulbs:</label>
              <input
                type="number"
                value={currentBulbs}
                onChange={(e) => setCurrentBulbs(parseInt(e.target.value))}
                className="w-full p-2 rounded bg-gray-800 text-white border border-gray-700"
                min="1"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-300 mb-1">LED replacement bulbs:</label>
              <input
                type="number"
                value={ledBulbs}
                onChange={(e) => setLedBulbs(parseInt(e.target.value))}
                className="w-full p-2 rounded bg-gray-800 text-white border border-gray-700"
                min="1"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-300 mb-1">Hours per day:</label>
              <input
                type="number"
                value={hoursPerDay}
                onChange={(e) => setHoursPerDay(parseInt(e.target.value))}
                className="w-full p-2 rounded bg-gray-800 text-white border border-gray-700"
                min="1"
                max="24"
              />
            </div>
            <button
              onClick={simulateEnergyEfficiency}
              disabled={loading}
              className="w-full bg-yellow-600 text-white py-2 px-4 rounded hover:bg-yellow-700 disabled:opacity-50"
            >
              {loading ? "Calculating..." : "Simulate"}
            </button>
          </div>

          {energyResult && (
            <div className="mt-4 p-3 bg-yellow-900/40 border border-yellow-700 rounded">
              <h4 className="font-semibold text-yellow-400">{energyResult.scenario}</h4>
              <p className="text-sm text-gray-300 mt-2">
                Annual energy savings: <strong>{energyResult.annual_energy_savings} kWh</strong>
                <br />
                Annual CO₂ savings: <strong>{energyResult.annual_co2_savings} kg</strong>
              </p>
            </div>
          )}
        </div>

        {/* Electric Vehicle */}
        <div className="border border-gray-700 bg-gray-900 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-4 text-purple-300">Switch to Electric Vehicle</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-300 mb-1">Annual kilometers:</label>
              <input
                type="number"
                value={annualKm}
                onChange={(e) => setAnnualKm(parseInt(e.target.value))}
                className="w-full p-2 rounded bg-gray-800 text-white border border-gray-700"
                min="1000"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-300 mb-1">Current fuel efficiency (L/100km):</label>
              <input
                type="number"
                value={fuelEfficiency}
                onChange={(e) => setFuelEfficiency(parseFloat(e.target.value))}
                className="w-full p-2 rounded bg-gray-800 text-white border border-gray-700"
                min="5"
                step="0.1"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-300 mb-1">EV efficiency (kWh/km):</label>
              <input
                type="number"
                value={evEfficiency}
                onChange={(e) => setEvEfficiency(parseFloat(e.target.value))}
                className="w-full p-2 rounded bg-gray-800 text-white border border-gray-700"
                min="0.1"
                step="0.1"
              />
            </div>
            <button
              onClick={simulateElectricVehicle}
              disabled={loading}
              className="w-full bg-purple-600 text-white py-2 px-4 rounded hover:bg-purple-700 disabled:opacity-50"
            >
              {loading ? "Calculating..." : "Simulate"}
            </button>
          </div>

          {evResult && (
            <div className="mt-4 p-3 bg-purple-900/40 border border-purple-700 rounded">
              <h4 className="font-semibold text-purple-400">{evResult.scenario}</h4>
              <p className="text-sm text-gray-300 mt-2">
                Annual CO₂ savings: <strong>{evResult.annual_co2_savings} kg</strong>
                <br />
                Current annual CO₂: <strong>{evResult.current_annual_co2} kg</strong>
                <br />
                New annual CO₂: <strong>{evResult.new_annual_co2} kg</strong>
              </p>
            </div>
          )}
        </div>

        {/* Local Food */}
        <div className="border border-gray-700 bg-gray-900 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-4 text-orange-300">Choose Local Food</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-300 mb-1">Imported meals per week:</label>
              <input
                type="number"
                value={importedMeals}
                onChange={(e) => setImportedMeals(parseInt(e.target.value))}
                className="w-full p-2 rounded bg-gray-800 text-white border border-gray-700"
                min="1"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-300 mb-1">Local reduction (%):</label>
              <input
                type="number"
                value={localReductionPercent}
                onChange={(e) => setLocalReductionPercent(parseInt(e.target.value))}
                className="w-full p-2 rounded bg-gray-800 text-white border border-gray-700"
                min="10"
                max="100"
              />
            </div>
            <button
              onClick={simulateLocalFood}
              disabled={loading}
              className="w-full bg-orange-600 text-white py-2 px-4 rounded hover:bg-orange-700 disabled:opacity-50"
            >
              {loading ? "Calculating..." : "Simulate"}
            </button>
          </div>

          {localFoodResult && (
            <div className="mt-4 p-3 bg-orange-900/40 border border-orange-700 rounded">
              <h4 className="font-semibold text-orange-400">{localFoodResult.scenario}</h4>
              <p className="text-sm text-gray-300 mt-2">
                Weekly CO₂ savings: <strong>{localFoodResult.weekly_co2_savings} kg</strong>
                <br />
                Annual CO₂ savings: <strong>{localFoodResult.annual_co2_savings} kg</strong>
              </p>
            </div>
          )}
        </div>

        {/* Waste Reduction */}
        <div className="border border-gray-700 bg-gray-900 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-4 text-red-300">Reduce Food Waste</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-300 mb-1">Current waste (kg/week):</label>
              <input
                type="number"
                value={wasteKgPerWeek}
                onChange={(e) => setWasteKgPerWeek(parseFloat(e.target.value))}
                className="w-full p-2 rounded bg-gray-800 text-white border border-gray-700"
                min="1"
                step="0.5"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-300 mb-1">Reduction (%):</label>
              <input
                type="number"
                value={wasteReductionPercent}
                onChange={(e) => setWasteReductionPercent(parseInt(e.target.value))}
                className="w-full p-2 rounded bg-gray-800 text-white border border-gray-700"
                min="10"
                max="80"
              />
            </div>
            <button
              onClick={simulateWasteReduction}
              disabled={loading}
              className="w-full bg-red-600 text-white py-2 px-4 rounded hover:bg-red-700 disabled:opacity-50"
            >
              {loading ? "Calculating..." : "Simulate"}
            </button>
          </div>

          {wasteResult && (
            <div className="mt-4 p-3 bg-red-900/40 border border-red-700 rounded">
              <h4 className="font-semibold text-red-400">{wasteResult.scenario}</h4>
              <p className="text-sm text-gray-300 mt-2">
                Annual waste reduction: <strong>{wasteResult.annual_waste_reduction} kg</strong>
                <br />
                Annual CO₂ savings: <strong>{wasteResult.annual_co2_savings} kg</strong>
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Virtual Tree Planting */}
      {isLoggedIn && (
        <div className="mt-8 border border-gray-700 bg-gray-900 rounded-lg p-6">
          <h3 className="text-xl font-semibold mb-4 text-green-400">🌳 Virtual Tree Planting</h3>
          <p className="text-sm text-gray-300 mb-4">
            Plant virtual trees to offset your carbon footprint! Each tree absorbs ~21kg CO₂ per year.
          </p>

          <div className="grid md:grid-cols-3 gap-6">
            {/* Planting Action */}
            <div>
              <p className="text-sm text-gray-400 mb-4">
                Based on your carbon footprint from uploaded receipts, we'll calculate the optimal
                number of trees to plant for full offset.
              </p>
              <button
                onClick={plantTrees}
                disabled={loading}
                className="w-full bg-green-600 text-white py-2 px-4 rounded hover:bg-green-700 disabled:opacity-50"
              >
                {loading ? "Calculating & Planting..." : "🌱 Calculate & Plant Trees"}
              </button>
            </div>

            {/* Credits */}
            <div className="bg-gray-800 p-4 rounded-lg shadow-sm">
              <h4 className="font-semibold text-green-400 mb-2">💰 EcoCredits</h4>
              <p className="text-2xl font-bold text-green-300">{userCredits} Credits</p>
              <p className="text-sm text-gray-400">
                Earn credits by uploading receipts with low carbon footprint
              </p>
              <p className="text-xs text-gray-500 mt-1">100 credits = 1 tree</p>
            </div>

            {/* User Offsets */}
            <div>
              {userOffsets && (
                <div className="bg-gray-800 p-4 rounded-lg shadow-sm">
                  <h4 className="font-semibold text-green-400 mb-2">Your Forest 🌳</h4>
                  <p className="text-2xl font-bold text-green-300">
                    {userOffsets.total_trees || 0} Trees
                  </p>
                  <p className="text-sm text-gray-400">
                    CO₂ offset: {userOffsets.total_offset || 0} kg/year
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {userOffsets.badge} - {userOffsets.level}
                  </p>
                </div>
              )}
            </div>
          </div>

          {offsetResult && (
            <div className="mt-4 p-4 bg-green-900/40 border border-green-700 rounded-lg">
              <h4 className="font-semibold text-green-400">🎉 Success!</h4>
              <p className="text-gray-300">{offsetResult.message}</p>
              <p className="text-sm text-gray-400 mt-1">
                Trees planted: <strong>{offsetResult.trees_planted}</strong>
                <br />
                Carbon footprint offset: <strong>{offsetResult.carbon_footprint_offset} kg CO₂</strong>
                <br />
                CO₂ offset per year: <strong>{offsetResult.co2_offset_kg} kg/year</strong>
                <br />
                New badge:{" "}
                <strong className="text-green-300">{offsetResult.badge.badge}</strong> (
                {offsetResult.badge.level})
              </p>
            </div>
          )}
        </div>
      )}

      {!isLoggedIn && (
        <div className="mt-8 p-4 bg-yellow-900/30 border border-yellow-600 rounded-lg">
          <p className="text-yellow-300">
            <strong>Please login</strong> to access virtual tree planting and track your carbon
            offset progress.
          </p>
        </div>
      )}
    </div>
  );
}
