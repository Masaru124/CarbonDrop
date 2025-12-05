import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Upload from "./Upload";

const History = () => {
  const [history, setHistory] = useState([]);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");
    setIsLoggedIn(!!token);
    if (token) {
      loadHistory();
    }
  }, []);

  const loadHistory = () => {
    const token = localStorage.getItem("token");
    if (!token) return;
    fetch("http://localhost:8000/footprint_history", {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => r.json())
      .then((d) => setHistory(d || []))
      .catch(() => {});
  };

  if (!isLoggedIn) {
    return (
      <main className="max-w-6xl mx-auto px-6 py-10">
        <h2 className="text-2xl font-semibold mb-6">History</h2>
        <div className="text-center">
          <p className="text-lg mb-4">
            Please login to view your receipt history.
          </p>
          <button
            onClick={() => navigate("/login")}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition"
          >
            Go to Login
          </button>
        </div>
      </main>
    );
  }

  return (
    <main className="max-w-6xl mx-auto px-6 py-10 text-white">

      {/* History Section */}
      <section className="mt-1">
        <h2 className="text-2xl font-semibold mb-6">History</h2>

        {history.length === 0 ? (
          <p className="text-gray-500 italic">No history yet.</p>
        ) : (
          <ul className="space-y-4">
            {history.map((h) => (
              <li
                key={h.id}
                className="p-4 border rounded shadow-sm bg-[#121212] hover:bg-gray-700 transition"
              >
                <div className="flex justify-between items-center">
                  <div className="flex flex-col">
                    <span className="text-sm text-gray-100">
                      {new Date(h.date).toLocaleString()}
                    </span>
                    <span className="text-xs text-gray-400">
                      📄 {h.document_type.charAt(0).toUpperCase() + h.document_type.slice(1)} • {h.items.length} items
                    </span>
                  </div>
                  <span className="text-lg font-medium text-green-600">
                    {h.total_footprint} kg CO₂
                  </span>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
};

export default History;
