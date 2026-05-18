import { useState } from "react";
import { useCarbonDashboard } from "../hooks/useCarbonBudgeting";
import { AlertCircle } from "lucide-react";
import CarbonCoach from "../components/CarbonCoach";
import ForecastGraph from "../components/ForecastGraph";
import SimulationTool from "../components/SimulationTool";
import ThirtyDayPlanView from "../components/ThirtyDayPlanView";
import Card from "../ui/Card";
import Spinner from "../ui/Spinner";

export default function InsightsPage() {
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
    simulationLoading,
    simulationError,
  } = useCarbonDashboard();

  const tabs = [
    { id: "coach", label: "🎯 Weekly Coach" },
    { id: "forecast", label: "📈 30-Day Forecast" },
    { id: "simulate", label: "🔄 What-If Simulator" },
    { id: "plan", label: "📋 30-Day Plan" },
  ];

  if (error) {
    return (
      <div className="p-4 md:p-6 max-w-6xl mx-auto">
        <Card className="border-red-700 bg-red-900/20">
          <div className="flex items-start gap-4">
            <AlertCircle className="text-red-500 flex-shrink-0 mt-1" size={24} />
            <div>
              <h3 className="text-lg font-bold text-red-400 mb-1">Error Loading Data</h3>
              <p className="text-sm text-red-200">{error}</p>
            </div>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-4 md:p-6 max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl md:text-3xl font-bold text-green-400 mb-2">
          Carbon AI Assistant
        </h1>
        <p className="text-gray-400">
          Get personalized insights, forecasts, and sustainability recommendations powered by AI
        </p>
      </div>

      <div className="flex flex-wrap gap-2 mb-6 border-b border-gray-800 pb-4">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-5 py-2 rounded-lg text-sm font-semibold transition ${
              activeTab === tab.id
                ? "bg-green-600 text-white shadow-sm"
                : "bg-gray-800 text-gray-300 hover:bg-gray-700"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {loading && (
        <div className="flex flex-col items-center justify-center py-20">
          <Spinner size="lg" />
          <p className="text-gray-400 mt-4">Loading your carbon insights...</p>
        </div>
      )}

      {!loading && (
        <div className="space-y-6">
          {activeTab === "coach" && <CarbonCoach budget={coach} />}
          {activeTab === "forecast" && (
            <div>
              <h2 className="text-xl font-bold mb-4 text-green-400">30-Day Carbon Forecast</h2>
              <ForecastGraph forecast={forecast} />
              {forecast?.summary && (
                <Card className="mt-4">
                  <p className="text-sm text-gray-300">{forecast.summary}</p>
                </Card>
              )}
            </div>
          )}
          {activeTab === "simulate" && (
            <div>
              <h2 className="text-xl font-bold mb-4 text-green-400">Lifestyle Impact Simulator</h2>
              <SimulationTool
                onSimulate={runSimulation}
                result={simulationResult}
                loading={simulationLoading}
                error={simulationError}
              />
            </div>
          )}
          {activeTab === "plan" && (
            <div>
              <h2 className="text-xl font-bold mb-4 text-green-400">Your 30-Day Sustainability Plan</h2>
              <ThirtyDayPlanView plan={thirtyDayPlan} />
            </div>
          )}
        </div>
      )}

      {!loading && insights && (
        <div className="mt-10 grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { label: "Daily Footprint", value: `${insights.average_daily_footprint?.toFixed(1) || "—"} kg` },
            { label: "Weekly Budget", value: `${coach?.weekly_budget?.toFixed(1) || "—"} kg/week` },
            { label: "30-Day Projection", value: `${forecast?.projected_monthly_total?.toFixed(0) || "—"} kg` },
          ].map((stat, i) => (
            <Card key={stat.label}>
              <p className="text-xs text-gray-500 font-semibold uppercase tracking-wider mb-1">{stat.label}</p>
              <p className={`text-2xl font-bold ${i === 0 ? "text-green-400" : i === 1 ? "text-green-300" : "text-green-200"}`}>
                {stat.value}
              </p>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
