import { useState, useEffect } from "react";
import { useCarbonDashboard } from "../hooks/useCarbonBudgeting";
import { AlertCircle, Loader } from "lucide-react";
import CarbonCoach from "./CarbonCoach";
import ForecastGraph from "./ForecastGraph";
import SimulationTool from "./SimulationTool";
import ThirtyDayPlanView from "./ThirtyDayPlanView";

export default function CarbonInsights() {
  const [activeTab, setActiveTab] = useState("coach");
  const {
    insights,
    forecast,
    coach,
    thirtyDayPlan,
    simulationResult,
    loading,
    error,
    runSimulation,
  } = useCarbonDashboard();

  if (error) {
    return (
      <div className="min-h-screen bg-gray-950 text-white p-6">
        <div className="max-w-6xl mx-auto">
          <div className="bg-red-900/30 border border-red-700 rounded-lg p-6 flex items-start gap-4">
            <AlertCircle
              className="text-red-500 flex-shrink-0 mt-1"
              size={24}
            />
            <div>
              <h3 className="text-xl font-semibold text-red-400 mb-2">
                Error Loading Data
              </h3>
              <p className="text-red-200">{error}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-green-400 mb-2">
            Carbon AI Assistant
          </h1>
          <p className="text-gray-400">
            Get personalized insights, forecasts, and sustainability
            recommendations powered by AI
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="flex flex-wrap gap-3 mb-8 border-b border-gray-800 pb-4">
          <button
            onClick={() => setActiveTab("coach")}
            className={`px-6 py-2 rounded-lg font-semibold transition ${
              activeTab === "coach"
                ? "bg-green-600 text-white"
                : "bg-gray-800 text-gray-300 hover:bg-gray-700"
            }`}
          >
            🎯 Weekly Coach
          </button>
          <button
            onClick={() => setActiveTab("forecast")}
            className={`px-6 py-2 rounded-lg font-semibold transition ${
              activeTab === "forecast"
                ? "bg-green-600 text-white"
                : "bg-gray-800 text-gray-300 hover:bg-gray-700"
            }`}
          >
            📈 30-Day Forecast
          </button>
          <button
            onClick={() => setActiveTab("simulate")}
            className={`px-6 py-2 rounded-lg font-semibold transition ${
              activeTab === "simulate"
                ? "bg-green-600 text-white"
                : "bg-gray-800 text-gray-300 hover:bg-gray-700"
            }`}
          >
            🔄 What-If Simulator
          </button>
          <button
            onClick={() => setActiveTab("plan")}
            className={`px-6 py-2 rounded-lg font-semibold transition ${
              activeTab === "plan"
                ? "bg-green-600 text-white"
                : "bg-gray-800 text-gray-300 hover:bg-gray-700"
            }`}
          >
            📋 30-Day Plan
          </button>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="flex items-center justify-center py-20">
            <div className="flex flex-col items-center gap-4">
              <Loader className="animate-spin text-green-400" size={48} />
              <p className="text-gray-400 text-lg">
                Loading your carbon insights...
              </p>
            </div>
          </div>
        )}

        {/* Content */}
        {!loading && (
          <div className="space-y-6">
            {/* Weekly Coach Tab */}
            {activeTab === "coach" && coach && (
              <div className="bg-gray-900 rounded-lg border border-gray-800 p-8">
                <CarbonCoach data={coach} />
              </div>
            )}

            {/* Forecast Tab */}
            {activeTab === "forecast" && forecast && (
              <div className="bg-gray-900 rounded-lg border border-gray-800 p-8">
                <h2 className="text-2xl font-bold mb-6 text-green-400">
                  30-Day Carbon Forecast
                </h2>
                <ForecastGraph data={forecast} />
                {forecast.summary && (
                  <div className="mt-6 p-4 bg-gray-800 rounded-lg">
                    <p className="text-gray-300">{forecast.summary}</p>
                  </div>
                )}
              </div>
            )}

            {/* Simulation Tab */}
            {activeTab === "simulate" && (
              <div className="bg-gray-900 rounded-lg border border-gray-800 p-8">
                <h2 className="text-2xl font-bold mb-6 text-green-400">
                  Lifestyle Impact Simulator
                </h2>
                <SimulationTool
                  onSimulate={runSimulation}
                  result={simulationResult}
                />
              </div>
            )}

            {/* 30-Day Plan Tab */}
            {activeTab === "plan" && thirtyDayPlan && (
              <div className="bg-gray-900 rounded-lg border border-gray-800 p-8">
                <h2 className="text-2xl font-bold mb-6 text-green-400">
                  Your 30-Day Sustainability Plan
                </h2>
                <ThirtyDayPlanView plan={thirtyDayPlan} />
              </div>
            )}
          </div>
        )}

        {/* Quick Stats */}
        {!loading && insights && (
          <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
              <h3 className="text-gray-400 text-sm font-semibold mb-2">
                CURRENT STATUS
              </h3>
              <p className="text-3xl font-bold text-green-400">
                {insights.average_daily_footprint?.toFixed(1) || "—"} kg
              </p>
              <p className="text-gray-500 text-sm mt-2">
                Daily Carbon Footprint
              </p>
            </div>
            <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
              <h3 className="text-gray-400 text-sm font-semibold mb-2">
                BUDGET STATUS
              </h3>
              <p className="text-3xl font-bold text-blue-400">
                {coach?.weekly_budget?.toFixed(1) || "—"} kg/week
              </p>
              <p className="text-gray-500 text-sm mt-2">Weekly Carbon Budget</p>
            </div>
            <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
              <h3 className="text-gray-400 text-sm font-semibold mb-2">
                FORECAST
              </h3>
              <p className="text-3xl font-bold text-purple-400">
                {forecast?.projected_monthly_total?.toFixed(0) || "—"} kg
              </p>
              <p className="text-gray-500 text-sm mt-2">30-Day Projection</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
