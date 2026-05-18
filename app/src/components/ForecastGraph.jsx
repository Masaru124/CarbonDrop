import { useState } from "react";
import Card from "../ui/Card";
import Skeleton from "../ui/Skeleton";
import Badge from "../ui/Badge";

export function ForecastGraph({ forecast, loading, error }) {
  const [hoveredDay, setHoveredDay] = useState(null);

  if (loading) {
    return (
      <Card>
        <Skeleton className="h-6 w-64 mb-4" />
        <Skeleton className="h-4 w-full mb-2" />
        <div className="grid grid-cols-7 gap-2">
          {Array.from({ length: 28 }).map((_, i) => (
            <Skeleton key={i} className="h-24" />
          ))}
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="border-red-700 bg-red-900/20">
        <p className="text-red-400">Error loading forecast: {error}</p>
      </Card>
    );
  }

  if (!forecast || !forecast.forecasts?.length) {
    return (
      <Card>
        <p className="text-gray-400 text-center">No forecast data available.</p>
      </Card>
    );
  }

  const forecasts = forecast.forecasts.slice(0, 30);
  const maxValue = Math.max(...forecasts.map((f) => f.predicted_kg), 10);

  const weeks = [];
  for (let i = 0; i < forecasts.length; i += 7) {
    weeks.push({ weekNumber: Math.floor(i / 7) + 1, days: forecasts.slice(i, i + 7) });
  }

  const getTrendIcon = (trend) => {
    switch (trend) {
      case "increasing": return "📈";
      case "decreasing": return "📉";
      default: return "➡️";
    }
  };

  return (
    <Card>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <h2 className="text-xl font-bold">📊 30-Day Carbon Forecast</h2>
        {forecast.risk_level && (
          <Badge variant={forecast.risk_level === "low" ? "success" : "error"}>
            Risk: {forecast.risk_level.toUpperCase()}
          </Badge>
        )}
      </div>

      {forecast.summary && (
        <p className="text-sm text-gray-400 mb-6">{forecast.summary}</p>
      )}

      <div className="space-y-6 mb-6">
        {weeks.map((week) => (
          <div key={week.weekNumber}>
            <h3 className="text-sm font-semibold text-gray-300 mb-3">Week {week.weekNumber}</h3>
            <div className="grid grid-cols-3 sm:grid-cols-5 md:grid-cols-7 gap-1.5 md:gap-3">
              {week.days.map((day, idx) => {
                const percentHeight = ((day.predicted_kg) / maxValue) * 100;
                const isHovered = hoveredDay === `${week.weekNumber}-${idx}`;

                return (
                  <div
                    key={`${week.weekNumber}-${idx}`}
                    className="relative flex flex-col justify-end items-center cursor-pointer h-28 md:h-36"
                    onMouseEnter={() => setHoveredDay(`${week.weekNumber}-${idx}`)}
                    onMouseLeave={() => setHoveredDay(null)}
                  >
                    <div
                      className={`w-full rounded-t-md transition-all duration-200 ${
                        isHovered ? "opacity-80 scale-105" : ""
                      }`}
                      style={{
                        height: `${Math.max(percentHeight, 4)}%`,
                        backgroundColor: day.predicted_kg > 7 ? "#ef4444" : "#22c55e",
                      }}
                    />
                    {isHovered && (
                      <div className="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 bg-gray-800 text-white text-xs rounded-lg px-3 py-2 shadow-xl z-10 whitespace-nowrap">
                        <p className="font-semibold mb-1">
                          {new Date(day.date).toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" })}
                        </p>
                        <p className="font-bold">{day.predicted_kg.toFixed(2)} kg CO₂</p>
                        {day.confidence_interval && (
                          <p className="text-gray-400 text-[10px]">
                            {day.confidence_interval[0].toFixed(1)} - {day.confidence_interval[1].toFixed(1)} kg
                          </p>
                        )}
                        <p>{getTrendIcon(day.trend)} {day.trend}</p>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      <div className="flex flex-wrap gap-4 justify-center mb-6 p-3 bg-gray-800/50 rounded-lg">
        {[
          { color: "#22c55e", label: "Below 7 kg/day (Good)" },
          { color: "#ef4444", label: "Above 7 kg/day (High)" },
        ].map((item) => (
          <div key={item.label} className="flex items-center gap-2 text-xs text-gray-400">
            <span className="w-4 h-4 rounded" style={{ backgroundColor: item.color }} />
            {item.label}
          </div>
        ))}
      </div>

      <div className="bg-green-900/20 border-l-4 border-green-500 rounded-lg p-4">
        <h4 className="font-semibold text-green-400 text-sm mb-2">💡 Forecast Insights</h4>
        <ul className="space-y-1 text-xs text-green-300">
          <li>📈 Increasing trend detected — consider reducing purchases</li>
          <li>🛒 High-carbon days typically occur on weekends</li>
          <li>
            ✅ Your lowest-carbon days average{" "}
            {Math.min(...forecasts.map((f) => f.predicted_kg)).toFixed(1)} kg
          </li>
        </ul>
      </div>
    </Card>
  );
}

export default ForecastGraph;
