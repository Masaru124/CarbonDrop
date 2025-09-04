import React, { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Chart from "chart.js/auto";

export default function Upload({ onUploaded, onCreditsUpdated }) {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loading, setLoading] = useState(false);
  const canvasRef = useRef(null);
  const chartRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");
    setIsLoggedIn(!!token);
  }, []);

  const upload = async () => {
    if (!file) return alert("Choose an image first");

    setLoading(true);
    const fd = new FormData();
    fd.append("file", file);

    const token = localStorage.getItem("token");
    if (!token) {
      alert("Please login to upload receipts.");
      navigate("/login");
      return;
    }

    try {
      const res = await fetch("http://localhost:8000/upload_receipt", {
        method: "POST",
        body: fd,
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!res.ok) {
        const err = await res.text();
        setLoading(false);
        return alert("Upload failed: " + err);
      }

      const data = await res.json();
      setResult(data);
      if (onUploaded) onUploaded(data);
      if (onCreditsUpdated) onCreditsUpdated();

      // Chart.js setup
      const labels = data.items.map((i) => i.matched_name || i.name);
      const values = data.items.map((i) => i.footprint);

      if (canvasRef.current) {
        const ctx = canvasRef.current.getContext("2d");
        if (chartRef.current) chartRef.current.destroy();

        chartRef.current = new Chart(ctx, {
          type: "bar",
          data: {
            labels,
            datasets: [
              {
                label: "Carbon Footprint (kg CO₂)",
                data: values,
                backgroundColor: "rgba(34,197,94,0.6)", // green bars
                borderColor: "rgba(34,197,94,1)",
                borderWidth: 1,
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { labels: { color: "#fff" } },
            },
            scales: {
              x: { ticks: { color: "#fff" } },
              y: { ticks: { color: "#fff" } },
            },
          },
        });
      }
    } catch (err) {
      alert("Something went wrong: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!isLoggedIn) {
    return (
      <section className="py-10 px-6 max-w-4xl mx-auto text-white text-center">
        <h2 className="text-3xl font-semibold mb-6">Upload Receipt</h2>
        <p className="text-lg mb-4">
          Login to upload your receipts and get insights into the carbon footprint of your purchases.
        </p>
        <button
          onClick={() => navigate("/login")}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition"
        >
          Go to Login
        </button>
      </section>
    );
  }

  return (
    <section className="py-10 px-6 max-w-6xl mx-auto text-white min-h-[80vh]">
      <h2 className="text-3xl font-bold text-center mb-4">
        Upload & Analyze Your Receipt
      </h2>
      <p className="text-center text-gray-300 max-w-2xl mx-auto mb-8">
        Upload a shopping receipt image to analyze the environmental impact of your purchases.
        We’ll scan each item, calculate its estimated carbon footprint, and give you both a
        detailed breakdown and a visual chart.
      </p>

      {/* Upload Box */}
      <div className="flex flex-col items-center gap-4 bg-[#121212] border border-gray-700 p-8 rounded-xl shadow-md">
        <input
          type="file"
          accept="image/*"
          onChange={(e) => setFile(e.target.files[0])}
          className="block w-full text-sm text-gray-400
                 file:mr-4 file:py-2 file:px-4
                 file:rounded-lg file:border-0
                 file:text-sm file:font-semibold
                 file:bg-green-600 file:text-white
                 hover:file:bg-green-700"
        />
        <button
          onClick={upload}
          disabled={loading}
          className="px-6 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition disabled:opacity-50"
        >
          {loading ? "Analyzing..." : "Upload & Analyze"}
        </button>
      </div>

      {/* Results Section */}
      {result && (
        <div className="mt-12">
          <h3 className="text-2xl font-semibold mb-4">Analysis Result</h3>
          <p className="mb-6 text-gray-300">
            Here’s a breakdown of your receipt’s carbon footprint. Items with the highest impact are highlighted.
          </p>

          {/* Total Badge */}
          <div className="mb-8">
            <span className="px-4 py-2 bg-green-700 text-white rounded-full font-semibold">
              🌍 Total Footprint: {result.total_footprint} kg CO₂
            </span>
          </div>

          {/* Table */}
          <div className="overflow-x-auto rounded-lg shadow">
            <table className="w-full text-left border-collapse">
              <thead className="bg-green-600 text-white">
                <tr>
                  <th className="px-4 py-3">Item</th>
                  <th className="px-4 py-3">Matched</th>
                  <th className="px-4 py-3">Qty</th>
                  <th className="px-4 py-3">kg CO₂</th>
                </tr>
              </thead>
              <tbody>
                {(() => {
                  const top3 = result.items
                    .slice()
                    .sort((a, b) => b.footprint - a.footprint)
                    .slice(0, 3)
                    .map((x) => x.name);

                  return result.items.map((it, idx) => {
                    const highlight = top3.includes(it.name);
                    return (
                      <tr
                        key={idx}
                        className={
                          "border-b border-gray-200 " +
                          (highlight ? "bg-green-200 font-bold" : "bg-gray-100")
                        }
                      >
                        <td className="px-4 py-2 text-gray-900">{it.name}</td>
                        <td className="px-4 py-2 text-gray-900">{it.matched_name}</td>
                        <td className="px-4 py-2 text-gray-900">
                          {it.qty} {it.unit}
                        </td>
                        <td className="px-4 py-2 text-gray-900">{it.footprint}</td>
                      </tr>
                    );
                  });
                })()}
              </tbody>
            </table>
          </div>

          {/* Chart */}
          <div className="py-10">
            <h1 className="text-2xl font-bold mb-2">Visual Representation</h1>
            <p className="text-gray-400 mb-6">
              Each bar shows the estimated CO₂ footprint of an item from your receipt.
            </p>
            <div className="bg-[#121212] rounded-xl p-6 shadow-md">
              <canvas
                ref={canvasRef}
                style={{ maxWidth: 1600, minHeight: 400 }}
                className="mx-auto"
              />
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
