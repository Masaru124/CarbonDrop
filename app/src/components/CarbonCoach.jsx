import Card from "../ui/Card";
import Skeleton from "../ui/Skeleton";

const statusConfig = {
  low: { color: "bg-green-500", label: "Good", message: "Great job! You're well under your budget. Keep it up!" },
  medium: { color: "bg-green-600", label: "On Track", message: "You're on track. Focus on mindful choices." },
  high: { color: "bg-green-700", label: "Approaching Limit", message: "You're approaching your budget. Make mindful choices." },
  exceeded: { color: "bg-red-500", label: "Exceeded", message: "You've exceeded your budget. Check out the recommendations below!" },
};

function getStatus(percent) {
  if (percent <= 50) return "low";
  if (percent <= 80) return "medium";
  if (percent < 100) return "high";
  return "exceeded";
}

export function CarbonCoachCard({ budget, loading, error }) {
  if (loading) {
    return (
      <Card>
        <Skeleton className="h-6 w-48 mb-4" />
        <div className="grid grid-cols-3 gap-4 mb-4">
          {[1, 2, 3].map((i) => <Skeleton key={i} className="h-20" />)}
        </div>
        <Skeleton className="h-4 w-full mb-2" />
        <Skeleton className="h-8 w-full mb-4" />
        <Skeleton className="h-4 w-3/4" />
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="border-red-700 bg-red-900/20">
        <p className="text-red-400">Error loading coach data: {error}</p>
      </Card>
    );
  }

  if (!budget) {
    return (
      <Card>
        <p className="text-gray-400 text-center">Upload receipts to get personalized recommendations.</p>
      </Card>
    );
  }

  const status = getStatus(budget.progress_percent);
  const config = statusConfig[status];

  return (
    <Card>
      <div className="flex items-center gap-2 mb-6">
        <span className="text-2xl">🧠</span>
        <h2 className="text-xl font-bold">Your Carbon Coach</h2>
        <span className={`ml-auto px-3 py-1 rounded-full text-xs font-semibold text-white ${config.color}`}>
          {config.label}
        </span>
      </div>

      <p className="text-sm text-gray-400 mb-6">
        {new Date(budget.week_start_date).toLocaleDateString()} - {new Date(budget.week_end_date).toLocaleDateString()}
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        {[
          { label: "Weekly Limit", value: `${budget.recommended_weekly_limit_kg} kg CO₂` },
          { label: "Daily Limit", value: `${budget.recommended_daily_limit_kg} kg CO₂` },
          { label: "Last Week Avg", value: `${budget.historical_weekly_avg} kg CO₂` },
        ].map((item) => (
          <div key={item.label} className="bg-white/10 rounded-lg p-4 text-center backdrop-blur-sm">
            <p className="text-xs text-white/70 uppercase tracking-wider mb-1">{item.label}</p>
            <p className="text-lg font-bold">{item.value}</p>
          </div>
        ))}
      </div>

      <div className="mb-6">
        <p className="text-sm font-semibold mb-2">Weekly Progress</p>
        <div className="w-full h-5 bg-gray-800 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-300 ${
              status === "exceeded" ? "bg-red-500" : status === "high" ? "bg-yellow-500" : "bg-green-500"
            }`}
            style={{ width: `${Math.min(budget.progress_percent, 100)}%` }}
          />
        </div>
        <p className="text-xs text-right mt-1 text-gray-400">
          {budget.progress_percent.toFixed(1)}% of budget used
        </p>
      </div>

      {budget.tradeoff_suggestions?.length > 0 && (
        <div className="mb-6">
          <h3 className="font-semibold mb-3">💡 Smart Tradeoffs</h3>
          <ul className="space-y-2">
            {budget.tradeoff_suggestions.map((s, idx) => (
              <li key={idx} className="bg-gray-800 rounded-lg px-4 py-2.5 text-sm text-gray-300">
                {s}
              </li>
            ))}
          </ul>
        </div>
      )}

      {budget.anomaly_insights?.length > 0 && (
        <div className="mb-6">
          <h3 className="font-semibold mb-3">⚠️ Unusual Activity</h3>
          <ul className="space-y-2">
            {budget.anomaly_insights.map((s, idx) => (
              <li key={idx} className="bg-amber-500/10 border border-amber-500/20 rounded-lg px-4 py-2.5 text-sm text-amber-200">
                {s}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className={`rounded-lg p-4 text-center text-sm ${
        status === "exceeded" ? "bg-red-500/20 text-red-300" :
        status === "high" ? "bg-red-500/10 text-red-200" :
        status === "medium" ? "bg-green-500/10 text-green-300" :
        "bg-green-500/20 text-green-300"
      }`}>
        {config.message}
      </div>
    </Card>
  );
}

export default CarbonCoachCard;
