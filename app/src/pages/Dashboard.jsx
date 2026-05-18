import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Line } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from "chart.js";
import { useAuth } from "../contexts/AuthContext";
import { api } from "../lib/api";
import Card from "../ui/Card";
import Button from "../ui/Button";
import Spinner from "../ui/Spinner";
import EmptyState from "../ui/EmptyState";
import { TreePine, Coins, Trophy, FlaskConical } from "lucide-react";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

export default function DashboardPage() {
  const { isAuthenticated } = useAuth();
  const [data, setData] = useState([]);
  const [userOffsets, setUserOffsets] = useState(null);
  const [userCredits, setUserCredits] = useState(0);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated) {
      setLoading(false);
      return;
    }
    const load = async () => {
      try {
        const [dashData, offsets, userData] = await Promise.all([
          api.get("/dashboard").catch(() => []),
          api.get("/user_offsets").catch(() => null),
          api.get("/auth/me").catch(() => ({ eco_credits: 0 })),
        ]);
        setData(Array.isArray(dashData) ? dashData : []);
        setUserOffsets(offsets);
        setUserCredits(userData.eco_credits || 0);
      } catch {
        // handled
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [isAuthenticated]);

  if (!isAuthenticated) {
    return (
      <div className="p-4 md:p-6">
        <EmptyState
          icon="🔒"
          title="My Carbon Dashboard"
          description="Please login to view your carbon footprint dashboard."
          action={
            <Button onClick={() => navigate("/login")}>Go to Login</Button>
          }
        />
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Spinner size="lg" />
      </div>
    );
  }

  const chartData = {
    labels: data.map((d) => d.month),
    datasets: [
      {
        label: "kg CO₂e",
        data: data.map((d) => d.total),
        borderColor: "#22c55e",
        backgroundColor: "rgba(34,197,94,0.1)",
        fill: true,
        tension: 0.4,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: { labels: { color: "#9ca3af" } },
    },
    scales: {
      x: { ticks: { color: "#6b7280" }, grid: { color: "#1f2937" } },
      y: { ticks: { color: "#6b7280" }, grid: { color: "#1f2937" } },
    },
  };

  const statCards = [
    {
      icon: TreePine,
      label: "Your Forest",
      value: `${userOffsets?.total_trees || 0} Trees`,
      sub: `Absorbing ${userOffsets?.total_offset || 0} kg CO₂/year`,
    },
    {
      icon: Coins,
      label: "EcoCredits",
      value: `${userCredits} Credits`,
      sub: "Earn credits by uploading receipts",
    },
    {
      icon: Trophy,
      label: "Achievement",
      value: userOffsets?.badge || "—",
      sub: `${userOffsets?.level || 0} Level`,
    },
    {
      icon: FlaskConical,
      label: "Quick Actions",
      value: "Simulator",
      sub: "Offset more CO₂",
      action: true,
    },
  ];

  return (
    <div className="p-4 md:p-6 max-w-6xl mx-auto">
      <h1 className="text-2xl md:text-3xl font-bold mb-6">My Carbon Dashboard</h1>

      <Card className="mb-8">
        <h2 className="text-lg font-semibold mb-4">Monthly Footprint Trend</h2>
        {data.length > 0 ? (
          <div className="w-full max-w-3xl mx-auto">
            <Line data={chartData} options={chartOptions} />
          </div>
        ) : (
          <p className="text-gray-400 text-center py-8">No data yet. Upload receipts to see your trend.</p>
        )}
        <div className="mt-6 flex justify-center">
          <Button
            variant="secondary"
            onClick={async () => {
              try {
                const blob = await api.get("/report/pdf");
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = "footprint_report.pdf";
                a.click();
              } catch {
                // handled
              }
            }}
          >
            Download PDF Report
          </Button>
        </div>
      </Card>

      {userOffsets && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
          {statCards.map((card, idx) => (
            <Card
              key={idx}
              className={`border-green-700/50 ${card.action ? "cursor-pointer hover:bg-gray-800/50 transition" : ""}`}
              onClick={card.action ? () => navigate("/simulator") : undefined}
            >
              <div className="flex items-center gap-2 mb-3">
                <card.icon className="h-5 w-5 text-green-400" />
                <h3 className="text-sm font-semibold text-green-400">{card.label}</h3>
              </div>
              <p className="text-2xl font-bold text-white">{card.value}</p>
              <p className="text-xs text-gray-400 mt-1">{card.sub}</p>
              {card.action && (
                <p className="text-xs text-green-400 mt-2">Click to visit &rarr;</p>
              )}
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
