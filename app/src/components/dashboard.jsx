import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Line } from "react-chartjs-2";

export default function Dashboard() {
  const [data, setData] = useState([]);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userOffsets, setUserOffsets] = useState(null);
  const [userCredits, setUserCredits] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");
    setIsLoggedIn(!!token);
    if (token) {
      fetch("http://localhost:8000/dashboard", {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then((res) => res.json())
        .then((data) => {
          if (Array.isArray(data)) {
            setData(data);
          } else {
            setData([]);
            console.error("Dashboard data is not an array:", data);
          }
        });

      // Fetch user offsets
      fetch("http://localhost:8000/user_offsets", {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then((res) => res.json())
        .then((offsets) => setUserOffsets(offsets))
        .catch((error) => console.error("Error fetching offsets:", error));

      // Fetch user credits
      fetch("http://localhost:8000/auth/me", {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then((res) => res.json())
        .then((userData) => setUserCredits(userData.eco_credits || 0))
        .catch((error) => console.error("Error fetching credits:", error));
    }
  }, []);

  // Add function to refresh user credits
  const refreshUserCredits = () => {
    const token = localStorage.getItem("token");
    if (!token) return;
    fetch("http://localhost:8000/auth/me", {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.json())
      .then((userData) => setUserCredits(userData.eco_credits || 0))
      .catch((error) => console.error("Error fetching credits:", error));
  };

  const downloadReport = () => {
    const token = localStorage.getItem("token");
    if (!token) return;
    fetch("http://localhost:8000/report/pdf", {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.blob())
      .then((blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "footprint_report.pdf";
        a.click();
      });
  };

  if (!isLoggedIn) {
    return (
      <div className="p-6">
        <h1 className="text-2xl font-bold">My Carbon Dashboard</h1>
        <div className="text-center">
          <p className="text-lg mb-4">
            Please login to view your carbon footprint dashboard.
          </p>
          <button
            onClick={() => navigate("/login")}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition"
          >
            Go to Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-[#111111] text-white min-h-screen mx-auto">
      <h1 className="text-2xl font-bold mb-4 text-center">
        My Carbon Dashboard
      </h1>

      {/* Line Chart */}
      <div className="w-[100vh] bg-[#1a1a1a] p-4 rounded mx-auto shadow">
        <Line
          data={{
            labels: data.map((d) => d.month),
            datasets: [
              {
                label: "kg CO₂e",
                data: data.map((d) => d.total),
                borderColor: "#22c55e", // Tailwind green-500
                backgroundColor: "rgba(34,197,94,0.2)",
              },
            ],
          }}
          options={{
            plugins: {
              legend: { labels: { color: "#fff" } },
            },
            scales: {
              x: { ticks: { color: "#aaa" }, grid: { color: "#333" } },
              y: { ticks: { color: "#aaa" }, grid: { color: "#333" } },
            },
          }}
        />
        <button
          onClick={downloadReport}
          className="mt-6 bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-900 shadow hover:transition-shadow"
        >
          Download PDF Report
        </button>
      </div>

      {/* Virtual Forest Section */}
      {userOffsets && (
        <div className="mt-8 grid md:grid-cols-4 gap-6">
          {/* Virtual Forest */}
          <div className="bg-[#1a1a1a] border border-green-700 rounded-xl p-6 shadow">
            <h3 className="text-lg font-semibold text-green-400 mb-2">
              🌳 Your Virtual Forest
            </h3>
            <p className="text-3xl font-bold text-green-500">
              {userOffsets.total_trees} Trees
            </p>
            <p className="text-sm text-green-300 mt-1">
              Absorbing {userOffsets.total_offset} kg CO₂/year
            </p>
          </div>

          {/* EcoCredits */}
          <div className="bg-[#1a1a1a] border border-yellow-700 rounded-xl p-6 shadow">
            <h3 className="text-lg font-semibold text-yellow-400 mb-2">
              💰 EcoCredits
            </h3>
            <p className="text-3xl font-bold text-yellow-500">
              {userCredits} Credits
            </p>
            <p className="text-sm text-yellow-300 mt-1">
              Earn credits by uploading receipts
            </p>
            <p className="text-xs text-yellow-400 mt-1">100 credits = 1 tree</p>
          </div>

          {/* Achievement Badge */}
          <div className="bg-[#1a1a1a] border border-blue-700 rounded-xl p-6 shadow">
            <h3 className="text-lg font-semibold text-blue-400 mb-2">
              🏆 Achievement Badge
            </h3>
            <p className="text-2xl font-bold text-blue-500">
              {userOffsets.badge}
            </p>
            <p className="text-sm text-blue-300 mt-1">
              {userOffsets.level} Level
            </p>
          </div>

          {/* Quick Actions */}
          <div className="bg-[#1a1a1a] border border-purple-700 rounded-xl p-6 shadow">
            <h3 className="text-lg font-semibold text-purple-400 mb-2">
              🎯 Quick Actions
            </h3>
            <button
              onClick={() => navigate("/simulator")}
              className="w-full bg-purple-600 text-white py-2 px-4 rounded-lg hover:bg-purple-700 transition shadow"
            >
              Plant More Trees
            </button>
            <p className="text-xs text-purple-300 mt-2">
              Visit the simulator to offset more CO₂
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
