import React, { useState, useEffect } from "react";
import Upload from "./Upload";

const History = () => {
  const [history, setHistory] = useState([]);

  const loadHistory = () => {
    fetch("http://localhost:8000/footprint_history")
      .then((r) => r.json())
      .then((d) => setHistory(d.history || []))
      .catch(() => {});
  };

  useEffect(() => {
    loadHistory();
  }, []);

  return (
    <main className="max-w-6xl mx-auto px-6 py-10">
      {/* Upload Component */}
      <Upload onUploaded={loadHistory} />

      {/* History Section */}
      <section className="mt-12">
        <h2 className="text-2xl font-semibold mb-6">History</h2>

        {history.length === 0 ? (
          <p className="text-gray-500 italic">No history yet.</p>
        ) : (
          <ul className="space-y-4">
            {history.map((h) => (
              <li
                key={h.id}
                className="p-4 border rounded-lg shadow-sm bg-white hover:bg-gray-50 transition"
              >
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">
                    {new Date(h.date).toLocaleString()}
                  </span>
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
