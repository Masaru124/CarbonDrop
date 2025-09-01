import { useState, useEffect } from "react";

export default function WhatIfSimulator() {
  const [meatMeals, setMeatMeals] = useState(3);
  const [weeks, setWeeks] = useState(52);
  const [meatResult, setMeatResult] = useState(null);
  const [trips, setTrips] = useState(4);
  const [distance, setDistance] = useState(500);
  const [fromMode, setFromMode] = useState('flight');
  const [toMode, setToMode] = useState('train');
  const [transportResult, setTransportResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // Offset related state
  const [offsetResult, setOffsetResult] = useState(null);
  const [userOffsets, setUserOffsets] = useState(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [carbonFootprint, setCarbonFootprint] = useState(0);
  const [userCredits, setUserCredits] = useState(0);

  const simulateMeatReplacement = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/simulate_meat_replacement', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ meat_meals_per_week: meatMeals, weeks })
      });
      const result = await response.json();
      setMeatResult(result);
    } catch (error) {
      console.error('Error simulating meat replacement:', error);
    }
    setLoading(false);
  };

  const simulateTransportSwitch = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/simulate_transport_switch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          trips_per_year: trips,
          distance_per_trip_km: distance,
          from_mode: fromMode,
          to_mode: toMode
        })
      });
      const result = await response.json();
      setTransportResult(result);
    } catch (error) {
      console.error('Error simulating transport switch:', error);
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
      const response = await fetch('http://localhost:8000/plant_trees', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });
      if (!response.ok) {
        const errorData = await response.json();
        alert(`Error planting trees: ${errorData.detail || 'Unknown error'}`);
        setLoading(false);
        return;
      }
      const result = await response.json();
      setOffsetResult(result);
      // Refresh user offsets and credits after planting
      fetchUserOffsets();
      fetchUserCredits();
    } catch (error) {
      console.error('Error planting trees:', error);
    }
    setLoading(false);
  };

  const fetchUserOffsets = async () => {
    const token = localStorage.getItem("token");
    if (!token) return;

    try {
      const response = await fetch('http://localhost:8000/user_offsets', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setUserOffsets(data);
    } catch (error) {
      console.error('Error fetching user offsets:', error);
    }
  };

  const fetchUserCredits = async () => {
    const token = localStorage.getItem("token");
    if (!token) return;

    try {
      const response = await fetch('http://localhost:8000/auth/me', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setUserCredits(data.eco_credits || 0);
    } catch (error) {
      console.error('Error fetching user credits:', error);
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
    <div className="p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-6 text-green-700">What-if Simulator</h2>

      <div className="grid md:grid-cols-2 gap-8">
        {/* Meat Replacement Scenario */}
        <div className="border rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-4">Replace Meat Meals with Plant-Based</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Meat meals per week:</label>
              <input
                type="number"
                value={meatMeals}
                onChange={(e) => setMeatMeals(parseInt(e.target.value))}
                className="w-full p-2 border rounded"
                min="1"
                max="21"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Weeks per year:</label>
              <input
                type="number"
                value={weeks}
                onChange={(e) => setWeeks(parseInt(e.target.value))}
                className="w-full p-2 border rounded"
                min="1"
                max="52"
              />
            </div>
            <button
              onClick={simulateMeatReplacement}
              disabled={loading}
              className="w-full bg-green-600 text-white py-2 px-4 rounded hover:bg-green-700 disabled:opacity-50"
            >
              {loading ? 'Calculating...' : 'Simulate'}
            </button>
          </div>

          {meatResult && (
            <div className="mt-4 p-3 bg-green-50 rounded">
              <h4 className="font-semibold text-green-800">{meatResult.scenario}</h4>
              <p className="text-sm text-green-700 mt-2">
                Weekly CO₂ savings: <strong>{meatResult.weekly_savings} kg</strong><br/>
                Annual CO₂ savings: <strong>{meatResult.annual_savings} kg</strong>
              </p>
            </div>
          )}
        </div>

        {/* Transport Switch Scenario */}
        <div className="border rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-4">Switch Transport Mode</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Trips per year:</label>
              <input
                type="number"
                value={trips}
                onChange={(e) => setTrips(parseInt(e.target.value))}
                className="w-full p-2 border rounded"
                min="1"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Distance per trip (km):</label>
              <input
                type="number"
                value={distance}
                onChange={(e) => setDistance(parseFloat(e.target.value))}
                className="w-full p-2 border rounded"
                min="1"
              />
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-sm font-medium mb-1">From:</label>
                <select
                  value={fromMode}
                  onChange={(e) => setFromMode(e.target.value)}
                  className="w-full p-2 border rounded"
                >
                  <option value="flight">Flight</option>
                  <option value="train">Train</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">To:</label>
                <select
                  value={toMode}
                  onChange={(e) => setToMode(e.target.value)}
                  className="w-full p-2 border rounded"
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
              {loading ? 'Calculating...' : 'Simulate'}
            </button>
          </div>

          {transportResult && (
            <div className="mt-4 p-3 bg-blue-50 rounded">
              <h4 className="font-semibold text-blue-800">{transportResult.scenario}</h4>
              <p className="text-sm text-blue-700 mt-2">
                Annual CO₂ savings: <strong>{transportResult.annual_savings} kg</strong><br/>
                Original annual CO₂: <strong>{transportResult.original_annual_co2} kg</strong><br/>
                New annual CO₂: <strong>{transportResult.new_annual_co2} kg</strong>
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Virtual Tree Planting Section */}
      {isLoggedIn && (
        <div className="mt-8 border rounded-lg p-6 bg-green-50">
          <h3 className="text-xl font-semibold mb-4 text-green-800">🌳 Virtual Tree Planting</h3>
          <p className="text-sm text-green-700 mb-4">
            Plant virtual trees to offset your carbon footprint! Each tree absorbs ~21kg CO₂ per year.
          </p>

          <div className="grid md:grid-cols-3 gap-6">
            <div>
              <p className="text-sm text-green-700 mb-4">
                Based on your carbon footprint from uploaded receipts, we'll calculate the optimal number of trees to plant for full offset.
              </p>
              <button
                onClick={plantTrees}
                disabled={loading}
                className="w-full bg-green-600 text-white py-2 px-4 rounded hover:bg-green-700 disabled:opacity-50"
              >
                {loading ? 'Calculating & Planting...' : '🌱 Calculate & Plant Trees'}
              </button>
            </div>

            <div>
              <div className="bg-white p-4 rounded-lg shadow-sm mb-4">
                <h4 className="font-semibold text-green-800 mb-2">💰 EcoCredits</h4>
                <p className="text-2xl font-bold text-green-600">{userCredits} Credits</p>
                <p className="text-sm text-green-700">
                  Earn credits by uploading receipts with low carbon footprint
                </p>
                <p className="text-xs text-green-600 mt-1">
                  100 credits = 1 tree
                </p>
              </div>
            </div>

            <div>
              {userOffsets && (
                <div className="bg-white p-4 rounded-lg shadow-sm">
                  <h4 className="font-semibold text-green-800 mb-2">Your Forest 🌳</h4>
                  <p className="text-2xl font-bold text-green-600">{userOffsets.total_trees || 0} Trees</p>
                  <p className="text-sm text-green-700">
                    CO₂ offset: {userOffsets.total_offset || 0} kg/year
                  </p>
                  <p className="text-xs text-green-600 mt-1">
                    {userOffsets.badge} - {userOffsets.level}
                  </p>
                </div>
              )}
            </div>
          </div>

          {offsetResult && (
            <div className="mt-4 p-4 bg-green-100 rounded-lg border border-green-300">
              <h4 className="font-semibold text-green-800">🎉 Success!</h4>
              <p className="text-green-700">{offsetResult.message}</p>
              <p className="text-sm text-green-600 mt-1">
                Trees planted: <strong>{offsetResult.trees_planted}</strong><br/>
                Carbon footprint offset: <strong>{offsetResult.carbon_footprint_offset} kg CO₂</strong><br/>
                CO₂ offset per year: <strong>{offsetResult.co2_offset_kg} kg/year</strong><br/>
                New badge: <strong>{offsetResult.badge.badge}</strong> ({offsetResult.badge.level})
              </p>
            </div>
          )}
        </div>
      )}

      {!isLoggedIn && (
        <div className="mt-8 p-4 bg-yellow-50 rounded-lg border border-yellow-300">
          <p className="text-yellow-800">
            <strong>Please login</strong> to access virtual tree planting and track your carbon offset progress.
          </p>
        </div>
      )}
    </div>
  );
}
