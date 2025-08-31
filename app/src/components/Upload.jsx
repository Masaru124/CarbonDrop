import React, { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Chart from "chart.js/auto";

export default function Upload({ onUploaded }) {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const canvasRef = useRef(null);
  const chartRef = useRef(null); // 👈 track chart instance
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");
    setIsLoggedIn(!!token);
  }, []);

  const upload = async () => {
    if (!file) return alert("Choose an image first");
    const fd = new FormData();
    fd.append("file", file);

    const token = localStorage.getItem("token");
    if (!token) {
      alert("Please login to upload receipts.");
      navigate("/login");
      return;
    }

    const res = await fetch("http://localhost:8000/upload_receipt", {
      method: "POST",
      body: fd,
      headers: {
        "Authorization": `Bearer ${token}`,
      },
    });

    if (!res.ok) {
      const err = await res.text();
      return alert("Upload failed: " + err);
    }

    const data = await res.json();
    setResult(data);
    if (onUploaded) onUploaded(data);

    // Chart.js setup
    const labels = data.items.map((i) => i.matched_name || i.name);
    const values = data.items.map((i) => i.footprint);

    if (canvasRef.current) {
      const ctx = canvasRef.current.getContext("2d");
      if (!ctx) return;

      // destroy old chart if it exists
      if (chartRef.current) {
        chartRef.current.destroy();
      }

      chartRef.current = new Chart(ctx, {
        type: "bar",
        data: {
          labels,
          datasets: [
            {
              label: "kg CO₂",
              data: values,
              borderColor: "rgba(75,192,192,1)",
              backgroundColor: "rgba(75,192,192,0.2)",
              fill: true,
              tension: 0.3, // smooth curves
            },
          ],
        },
        options: { responsive: true, maintainAspectRatio: false },
      });
    }
  };

  if (!isLoggedIn) {
    return (
      <section className="upload-card py-10 px-6 max-w-6xl mx-auto">
        <h2 className="text-3xl font-semibold text-center mb-8">
          Upload Receipt
        </h2>
        <div className="text-center">
          <p className="text-lg mb-4">Please login to upload and analyze receipts.</p>
          <button
            onClick={() => navigate("/login")}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition"
          >
            Go to Login
          </button>
        </div>
      </section>
    );
  }

  return (
    <section className="upload-card py-10 px-6 max-w-6xl mx-auto">
      <h2 className="text-3xl font-semibold text-center mb-8">
        Upload Receipt
      </h2>

      {/* Upload Box */}
      <div className="flex flex-col items-center gap-4 bg-gray-50 p-8 rounded-2xl shadow-md">
        <input
          type="file"
          accept="image/*"
          onChange={(e) => setFile(e.target.files[0])}
          className="block w-full text-sm text-gray-500
                 file:mr-4 file:py-2 file:px-4
                 file:rounded-lg file:border-0
                 file:text-sm file:font-semibold
                 file:bg-green-600 file:text-white
                 hover:file:bg-green-700"
        />
        <button
          onClick={upload}
          className="px-6 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition"
        >
          Upload & Analyze
        </button>
      </div>

      {/* Result Section */}
      {result && (
        <div className="result mt-12">
          <h3 className="text-2xl font-semibold mb-6">
            Result — Total:{" "}
            <span className="text-green-600">
              {result.total_footprint} kg CO₂
            </span>
          </h3>

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
                          "odd:bg-white even:bg-gray-50 hover:bg-gray-100 " +
                          (highlight ? "bg-red-100 font-bold" : "")
                        }
                      >
                        <td className="px-4 py-2">{it.name}</td>
                        <td className="px-4 py-2">{it.matched_name}</td>
                        <td className="px-4 py-2">{it.qty} {it.unit}</td>
                        <td className="px-4 py-2">{it.footprint}</td>
                      </tr>
                    );
                  });
                })()}
              </tbody>
            </table>
          </div>

          <div className="py-10">
            <h1 className="text-2xl font-sans font-semibold">Visual Representation</h1>
            <canvas
              ref={canvasRef}
              style={{ maxWidth: 1600, minHeight: 400, marginTop: 20 }}
              className="mx-auto"
            />
          </div>
        </div>
      )}
    </section>
  );
}
