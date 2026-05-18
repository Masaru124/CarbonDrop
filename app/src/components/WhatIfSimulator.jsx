import { useEffect, useState } from "react";
import { useAuth } from "../contexts/AuthContext";
import { api } from "../lib/api";
import { useToast } from "../ui/Toast";
import Button from "../ui/Button";
import Card from "../ui/Card";
import MeatSimulator from "./simulators/MeatSimulator";
import TransportSimulator from "./simulators/TransportSimulator";
import EnergySimulator from "./simulators/EnergySimulator";
import EVSimulator from "./simulators/EVSimulator";
import LocalFoodSimulator from "./simulators/LocalFoodSimulator";
import WasteSimulator from "./simulators/WasteSimulator";

export default function WhatIfSimulator() {
  const { isAuthenticated } = useAuth();
  const toast = useToast();
  const [userOffsets, setUserOffsets] = useState(null);
  const [userCredits, setUserCredits] = useState(0);
  const [loading, setLoading] = useState(false);
  const [offsetResult, setOffsetResult] = useState(null);

  useEffect(() => {
    if (isAuthenticated) {
      api.get("/user_offsets").then(setUserOffsets).catch(() => {});
      api.get("/auth/me").then((d) => setUserCredits(d.eco_credits || 0)).catch(() => {});
    }
  }, [isAuthenticated]);

  const plantTrees = async () => {
    setLoading(true);
    try {
      const result = await api.post("/plant_trees");
      setOffsetResult(result);
      toast("Trees planted successfully!", "success");
      const [offsets, userData] = await Promise.all([
        api.get("/user_offsets"),
        api.get("/auth/me"),
      ]);
      setUserOffsets(offsets);
      setUserCredits(userData.eco_credits || 0);
    } catch (err) {
      toast(err.message || "Error planting trees", "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-green-400">What-if Simulator</h2>
          <p className="text-gray-400 text-sm mt-1">See how different lifestyle changes can reduce your carbon footprint.</p>
        </div>
        <div className="grid md:grid-cols-2 gap-5">
          <MeatSimulator />
          <TransportSimulator />
          <EnergySimulator />
          <EVSimulator />
          <LocalFoodSimulator />
          <WasteSimulator />
        </div>
      </div>

      {isAuthenticated && (
        <Card className="border-green-800/60">
          <div className="flex items-center gap-3 mb-5">
            <span className="text-2xl">🌳</span>
            <div>
              <h3 className="text-lg font-semibold text-green-400">Virtual Tree Planting</h3>
              <p className="text-xs text-gray-400">Each tree absorbs ~21kg CO₂ per year</p>
            </div>
          </div>

          <div className="grid md:grid-cols-3 gap-5">
            <div className="md:col-span-2">
              <p className="text-sm text-gray-400 mb-4">
                Use your earned EcoCredits to plant virtual trees and offset your carbon footprint.
              </p>
              <Button onClick={plantTrees} loading={loading} className="w-full md:w-auto">
                Calculate &amp; Plant Trees
              </Button>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="bg-gray-800/60 rounded-lg p-4 text-center">
                <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">Credits</p>
                <p className="text-2xl font-bold text-green-400">{userCredits}</p>
                <p className="text-[10px] text-gray-500 mt-1">100 = 1 tree</p>
              </div>
              <div className="bg-gray-800/60 rounded-lg p-4 text-center">
                <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">Forest</p>
                <p className="text-2xl font-bold text-green-400">{userOffsets?.total_trees || 0}</p>
                <p className="text-[10px] text-gray-500 mt-1">trees planted</p>
              </div>
            </div>
          </div>

          {userOffsets && userOffsets.total_trees > 0 && (
            <div className="mt-4 flex flex-wrap items-center gap-3 text-xs text-gray-400 bg-gray-800/30 rounded-lg px-4 py-2.5">
              <span>CO₂ offset: <strong className="text-white">{userOffsets.total_offset} kg/year</strong></span>
              <span className="hidden sm:inline text-gray-600">|</span>
              <span>Badge: <strong className="text-green-300">{userOffsets.badge}</strong> ({userOffsets.level})</span>
            </div>
          )}

          {offsetResult && (
            <div className="mt-4 p-4 bg-green-950/50 border border-green-800 rounded-lg animate-fade-in">
              <p className="font-semibold text-green-400 text-sm mb-2">Success!</p>
              <p className="text-sm text-gray-300">{offsetResult.message}</p>
              <div className="mt-2 text-xs text-gray-400 space-y-0.5">
                <p>Trees: <strong className="text-white">{offsetResult.trees_planted}</strong></p>
                <p>CO₂ offset: <strong className="text-white">{offsetResult.carbon_footprint_offset} kg</strong></p>
              </div>
            </div>
          )}
        </Card>
      )}

      {!isAuthenticated && (
        <div className="p-5 bg-gray-900/50 border border-gray-800 rounded-xl text-center">
          <p className="text-gray-400 text-sm">
            <span className="text-white font-medium">Login</span> to access virtual tree planting and track your carbon offset progress.
          </p>
        </div>
      )}
    </div>
  );
}
