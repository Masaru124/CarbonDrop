import { useState } from "react";
import Card from "../ui/Card";
import Skeleton from "../ui/Skeleton";
import Badge from "../ui/Badge";

const tabs = ["overview", "daily-plan", "recipes", "commute", "habits"];

export function ThirtyDayPlanView({ plan, loading, error }) {
  const [activeTab, setActiveTab] = useState("overview");
  const [expandedDay, setExpandedDay] = useState(null);
  const [completedDays, setCompletedDays] = useState(new Set());

  const toggleDay = (day) => {
    const next = new Set(completedDays);
    if (next.has(day)) next.delete(day);
    else next.add(day);
    setCompletedDays(next);
  };

  if (loading) {
    return (
      <Card>
        <Skeleton className="h-6 w-64 mb-4" />
        <Skeleton className="h-20 w-full mb-4" />
        <div className="grid grid-cols-5 gap-2">
          {Array.from({ length: 10 }).map((_, i) => (
            <Skeleton key={i} className="h-16" />
          ))}
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="border-red-700 bg-red-900/20">
        <p className="text-red-400">Error loading plan: {error}</p>
      </Card>
    );
  }

  if (!plan) {
    return (
      <Card>
        <p className="text-gray-400 text-center">No plan available. Upload receipts first.</p>
      </Card>
    );
  }

  const completionPercent = completedDays.size > 0 ? (completedDays.size / 30) * 100 : 0;

  return (
    <Card>
      <div className="text-center mb-6 pb-4 border-b border-gray-800">
        <h2 className="text-2xl font-bold mb-1">🌱 Your 30-Day Sustainability Plan</h2>
        <p className="text-sm text-gray-400">
          {new Date(plan.start_date).toLocaleDateString()} - {new Date(plan.end_date).toLocaleDateString()}
        </p>
      </div>

      <div className="bg-gradient-to-br from-green-700 to-green-900 rounded-lg p-6 mb-6 text-white">
        <h3 className="font-semibold mb-2">Summary</h3>
        <p className="text-sm text-green-100 mb-4">{plan.summary}</p>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {[
            { label: "Current Weekly Avg", value: `${plan.current_weekly_avg_kg} kg`, color: "text-green-200" },
            { label: "Target After 30 Days", value: `${plan.target_weekly_avg_kg} kg`, color: "text-white" },
            { label: "Potential Savings", value: `${plan.total_potential_savings_kg} kg`, color: "text-green-200" },
          ].map((m) => (
            <div key={m.label} className="bg-white/10 rounded-lg p-3 text-center">
              <p className="text-xs text-white/80 uppercase tracking-wider mb-1">{m.label}</p>
              <p className={`text-lg font-bold ${m.color}`}>{m.value}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="flex gap-1 overflow-x-auto pb-3 mb-4 border-b border-gray-800">
        {tabs.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition ${
              activeTab === tab ? "bg-green-600 text-white" : "text-gray-400 hover:text-white hover:bg-gray-800"
            }`}
          >
            {tab.split("-").join(" ").toUpperCase()}
          </button>
        ))}
      </div>

      <div className="animate-fade-in">
        {activeTab === "overview" && (
          <div className="space-y-6">
            {plan.problem_areas?.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold mb-4">🎯 Top 3 Problem Areas</h3>
                <div className="grid sm:grid-cols-3 gap-4">
                  {plan.problem_areas.map((area, idx) => (
                    <div key={idx} className="bg-gray-800/50 border-l-4 border-red-500 rounded-lg p-4">
                      <p className="font-medium text-sm mb-2">{idx + 1}. {area.category?.toUpperCase()}</p>
                      <p className="text-xl font-bold text-red-400">{area.total_kg} kg CO₂</p>
                      <p className="text-xs text-gray-400">{area.percentage}% of total</p>
                      <p className="text-xs text-gray-500">{area.item_count} items</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {plan.improvement_checklist?.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold mb-4">✅ Improvement Checklist</h3>
                <ul className="space-y-2">
                  {plan.improvement_checklist.map((item, idx) => (
                    <li key={idx} className="bg-gray-800/30 border-l-4 border-green-500 rounded-lg px-4 py-3 text-sm text-gray-300">
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {activeTab === "daily-plan" && (
          <div className="space-y-4">
            {completedDays.size > 0 && (
              <div>
                <p className="text-sm font-medium text-gray-300 mb-2">Overall Progress</p>
                <div className="w-full h-4 bg-gray-800 rounded-full overflow-hidden">
                  <div className="h-full bg-green-500 rounded-full transition-all" style={{ width: `${completionPercent}%` }} />
                </div>
                <p className="text-xs text-gray-400 mt-1">{completedDays.size} of 30 days completed</p>
              </div>
            )}
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
              {plan.daily_plan?.map((day) => (
                <div
                  key={day.day}
                  onClick={() => setExpandedDay(expandedDay === day.day ? null : day.day)}
                  className={`relative bg-gray-800/50 rounded-lg p-3 cursor-pointer border-2 transition ${
                    completedDays.has(day.day) ? "border-green-600 bg-green-900/20" : "border-transparent hover:border-gray-600"
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-bold text-sm">Day {day.day}</span>
                    <span className={`w-3 h-3 rounded-full bg-green-500`} />
                  </div>
                  <p className="text-xs text-gray-400 truncate">{day.focus_area}</p>

                  {expandedDay === day.day && (
                    <div className="absolute top-full left-0 right-0 mt-2 bg-gray-800 border border-gray-700 rounded-lg p-4 z-10 shadow-xl">
                      <p className="font-medium text-sm mb-2 text-white">{day.action}</p>
                      {day.carbon_saved_vs_typical_kg && (
                        <p className="text-xs text-green-400 mb-2">Saves ~{day.carbon_saved_vs_typical_kg} kg CO₂</p>
                      )}
                      <button
                        onClick={(e) => { e.stopPropagation(); toggleDay(day.day); }}
                        className={`w-full py-1.5 rounded text-xs font-semibold transition ${
                          completedDays.has(day.day) ? "bg-green-600 text-white" : "bg-gray-700 text-gray-300 hover:bg-gray-600"
                        }`}
                      >
                        {completedDays.has(day.day) ? "✅ Completed" : "Mark Complete"}
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === "recipes" && (
          <div>
            <h3 className="text-lg font-semibold mb-4 text-green-400">🍱 Low-Carbon Recipes</h3>
            <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-4">
              {plan.recipes?.map((recipe, idx) => (
                <div key={idx} className="bg-gray-800/50 border-t-4 border-green-600 rounded-lg p-4">
                  <h4 className="font-semibold mb-3 text-white">{recipe.name}</h4>
                  <div className="grid grid-cols-3 gap-2 mb-3 text-center text-xs">
                    <div>
                      <p className="text-gray-500">Carbon</p>
                      <p className="font-bold text-white">{recipe.carbon_footprint_kg} kg</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Protein</p>
                      <p className="font-bold text-white">{recipe.protein_g}g</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Prep</p>
                      <p className="font-bold text-white">{recipe.prep_time_minutes}m</p>
                    </div>
                  </div>
                  <div className="bg-green-900/30 text-green-400 text-xs font-semibold text-center py-1.5 rounded mb-2">
                    💚 Saves {recipe.savings_vs_typical_kg} kg vs typical meal
                  </div>
                  <p className="text-xs text-gray-500">
                    <strong>Ingredients:</strong> {recipe.ingredients?.join(", ")}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === "commute" && (
          <div>
            <h3 className="text-lg font-semibold mb-4 text-green-400">🚗 Commute Alternatives</h3>
            <div className="space-y-4">
              {plan.commute_alternatives?.map((option, idx) => (
                <div key={idx} className="bg-gray-800/50 border-l-4 border-green-500 rounded-lg p-4">
                  <h4 className="font-semibold mb-3 text-white">{option.mode}</h4>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center text-sm">
                    <div>
                      <p className="text-gray-500 text-xs">Annual CO₂</p>
                      <p className="font-bold text-white">{option.annual_carbon_kg.toFixed(0)} kg</p>
                    </div>
                    <div>
                      <p className="text-gray-500 text-xs">Monthly Cost</p>
                      <p className="font-bold text-white">${option.cost_per_month.toFixed(0)}</p>
                    </div>
                    <div>
                      <p className="text-gray-500 text-xs">Time/Day</p>
                      <p className="font-bold text-white">{option.time_per_day_minutes} min</p>
                    </div>
                    <div>
                      <p className="text-gray-500 text-xs">Feasibility</p>
                      <p className="font-bold text-green-400">{(option.feasibility_score * 10).toFixed(0)}%</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === "habits" && (
          <div className="space-y-6">
            {plan.habit_changes?.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold mb-4 text-green-400">🔄 Recommended Habit Changes</h3>
                <ul className="space-y-2">
                  {plan.habit_changes.map((change, idx) => (
                    <li key={idx} className="bg-gray-800/30 border-l-4 border-green-500 rounded-lg px-4 py-3 text-sm text-gray-300">
                      {change}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {plan.subscriptions_to_replace?.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold mb-4 text-green-400">📦 Subscriptions to Replace</h3>
                <div className="grid sm:grid-cols-2 gap-4">
                  {plan.subscriptions_to_replace.map((sub, idx) => (
                    <div key={idx} className="bg-gray-800/50 border-l-4 border-green-500 rounded-lg p-4">
                      <h4 className="font-semibold text-white">{sub.item_name}</h4>
                      <p className="text-xs text-gray-400 mb-3">{sub.frequency}</p>
                      <div className="grid grid-cols-2 gap-3 text-center text-sm mb-3">
                        <div>
                          <p className="text-gray-500 text-xs">Annual CO₂</p>
                          <p className="font-bold text-white">{sub.annual_carbon_kg.toFixed(1)} kg</p>
                        </div>
                        <div>
                          <p className="text-gray-500 text-xs">Savings</p>
                          <p className="font-bold text-green-400">{sub.potential_savings_kg.toFixed(1)} kg</p>
                        </div>
                      </div>
                      <div className="bg-gray-900 rounded px-3 py-2 text-xs text-gray-400">
                        <strong className="text-white">Try:</strong> {sub.alternative}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </Card>
  );
}

export default ThirtyDayPlanView;
