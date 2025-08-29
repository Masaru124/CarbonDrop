import React, { useState, useRef } from "react";
import Chart from "chart.js/auto";
export default function Upload({ onUploaded }) {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const canvasRef = useRef(null);
  const upload = async () => {
    if (!file) return alert("Choose an image first");
    const fd = new FormData();
    fd.append("file", file);
    const res = await fetch("http://localhost:8000/upload_receipt", {
      method: "POST",
      body: fd,
    });
    if (!res.ok) {
      const err = await res.text();
      return alert("Upload failed: " + err);
    }
    const data = await res.json();
    setResult(data);
    if (onUploaded) onUploaded(data);
    const labels = data.items.map((i) => i.matched_name || i.name);
    const values = data.items.map((i) => i.footprint);
    if (canvasRef.current) {
      new Chart(canvasRef.current.getContext("2d"), {
        type: "bar",
        data: { labels, datasets: [{ label: "kg CO₂", data: values }] },
        options: { responsive: true },
      });
    }
  };
  return (
    <section className="upload-card">
      <h2>Upload Receipt</h2>
      <input
        type="file"
        accept="image/*"
        onChange={(e) => setFile(e.target.files[0])}
      />
      <button onClick={upload}>Upload & Analyze</button>
      {result && (
        <div className="result">
          <h3>Result — Total: {result.total_footprint} kg CO₂</h3>
          <table>
            <thead>
              <tr>
                <th>Item</th>
                <th>Matched</th>
                <th>Qty</th>
                <th>kg CO₂</th>
              </tr>
            </thead>
            <tbody>
              {result.items.map((it, idx) => (
                <tr key={idx}>
                  <td title={it.raw_line}>{it.name}</td>
                  <td>
                    {it.matched_name || "—"} ({it.match_score || 0})
                  </td>
                  <td>
                    {it.qty} {it.unit || ""}
                  </td>
                  <td>{it.footprint}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <canvas ref={canvasRef} style={{ maxWidth: 600, marginTop: 12 }} />
        </div>
      )}
    </section>
  );
}
