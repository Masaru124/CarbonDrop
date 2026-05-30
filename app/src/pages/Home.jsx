import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Chart from "chart.js/auto";
import { useAuth } from "../contexts/AuthContext";
import { api } from "../lib/api";
import { useToast } from "../ui/Toast";
import Button from "../ui/Button";
import Card from "../ui/Card";
import Badge from "../ui/Badge";
import Spinner from "../ui/Spinner";
import EmptyState from "../ui/EmptyState";
import { Upload as UploadIcon, FileText, BarChart3 } from "lucide-react";

export default function HomePage() {
  const { isAuthenticated } = useAuth();
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const canvasRef = useRef(null);
  const chartRef = useRef(null);
  const toast = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    return () => {
      if (chartRef.current) chartRef.current.destroy();
    };
  }, []);

  const upload = async () => {
    if (!file) {
      toast("Please select an image first", "warning");
      return;
    }

    setLoading(true);
    const fd = new FormData();
    fd.append("file", file);

    try {
      const data = await api.post("/upload_receipt", fd);
      const normalizedItems = Array.isArray(data.items) ? data.items.filter(Boolean) : [];
      const normalizedResult = { ...data, items: normalizedItems };
      setResult(normalizedResult);
      toast("Receipt analyzed successfully!", "success");

      if (canvasRef.current) {
        const ctx = canvasRef.current.getContext("2d");
        if (chartRef.current) chartRef.current.destroy();

        const labels = normalizedItems.map((i) => `${i.matched_name || i.name || "Item"} (${i.category || "food"})`);
        const values = normalizedItems.map((i) => i.footprint || 0);

        chartRef.current = new Chart(ctx, {
          type: "bar",
          data: {
            labels,
            datasets: [
              {
                label: "Carbon Footprint (kg CO₂)",
                data: values,
                backgroundColor: (context) => {
                    const item = normalizedItems[context.dataIndex];
                    if (!item) return "rgba(34, 197, 94, 0.6)";
                  const cat = item.category || "food";
                  const colors = {
                    transport: "rgba(59, 130, 246, 0.6)",
                    energy: "rgba(245, 158, 11, 0.6)",
                    utility: "rgba(139, 69, 19, 0.6)",
                    food: "rgba(34, 197, 94, 0.6)",
                  };
                  return colors[cat] || colors.food;
                },
                borderColor: (context) => {
                    const item = normalizedItems[context.dataIndex];
                    if (!item) return "rgba(34, 197, 94, 1)";
                  const cat = item.category || "food";
                  const colors = {
                    transport: "rgba(59, 130, 246, 1)",
                    energy: "rgba(245, 158, 11, 1)",
                    utility: "rgba(139, 69, 19, 1)",
                    food: "rgba(34, 197, 94, 1)",
                  };
                  return colors[cat] || colors.food;
                },
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
              x: { ticks: { color: "#fff", maxRotation: 45 } },
              y: { ticks: { color: "#fff" } },
            },
          },
        });
      }
    } catch (err) {
      toast(err.message || "Upload failed", "error");
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="p-4 md:p-6 max-w-4xl mx-auto">
        <EmptyState
          icon="📄"
          title="Upload Receipt"
          description="Login to upload your receipts and get insights into the carbon footprint of your purchases."
          action={<Button onClick={() => navigate("/login")}>Go to Login</Button>}
        />
      </div>
    );
  }

  const matched = result
    ? result.items.filter((it) => it && it.matched_name && it.matched_name !== "No match").length
    : 0;
  const total = result ? result.items.length : 0;
  const matchRate = total > 0 ? Math.round((matched / total) * 100) : 0;

  return (
    <div className="p-4 md:p-6 max-w-6xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-2xl md:text-3xl font-bold mb-2">
          Upload &amp; Analyze Your Receipt
        </h1>
        <p className="text-gray-400 max-w-2xl mx-auto">
          Upload receipts, utility bills, or invoices to analyze their environmental impact.
        </p>
      </div>

      <Card className="max-w-2xl mx-auto mb-8">
        <div className="flex flex-col items-center gap-4">
          <div className="w-full">
            <label className="flex flex-col items-center gap-3 p-8 border-2 border-dashed border-gray-700 rounded-xl cursor-pointer hover:border-green-500/50 transition">
              <UploadIcon className="h-10 w-10 text-gray-500" />
              <span className="text-sm text-gray-400">
                {file ? file.name : "Drop a receipt image here or click to browse"}
              </span>
              <input
                type="file"
                accept="image/*"
                onChange={(e) => setFile(e.target.files[0])}
                className="hidden"
              />
            </label>
          </div>
          <Button onClick={upload} disabled={loading || !file} loading={loading} size="lg">
            {loading ? "Analyzing..." : "Upload & Analyze"}
          </Button>
        </div>
      </Card>

      {result && (
        <div className="space-y-6 animate-fade-in">
          <Card>
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
              <div>
                <h2 className="text-xl font-bold">Analysis Result</h2>
                <p className="text-sm text-gray-400 mt-1">
                  Breakdown of your {result.document_type}&apos;s carbon footprint
                </p>
              </div>
              <Badge variant="info" className="text-sm px-3 py-1">
                <FileText className="h-4 w-4 mr-1" />
                {result.document_type?.charAt(0).toUpperCase() + result.document_type?.slice(1)}
              </Badge>
            </div>

            <div className="bg-gray-800/50 rounded-lg p-4 mb-6">
              <p className="text-sm font-medium text-gray-300 mb-2">Matching Performance</p>
              <div className="flex items-center gap-3">
                <span className="text-sm text-gray-400">
                  Match Rate: <strong className="text-white">{matchRate}%</strong> ({matched}/{total} items)
                </span>
                <Badge
                  variant={matchRate >= 80 ? "success" : matchRate >= 60 ? "warning" : "danger"}
                >
                  {matchRate >= 80 ? "Excellent" : matchRate >= 60 ? "Good" : "Needs Improvement"}
                </Badge>
                {result.parse_confidence && (
                  <Badge variant={result.parse_confidence === "high" ? "success" : result.parse_confidence === "medium" ? "warning" : "danger"}>
                    Parser {result.parse_confidence}
                  </Badge>
                )}
              </div>
              <div className="mt-3 flex flex-wrap gap-2 text-xs text-gray-400">
                {result.parser_used && <span className="px-2 py-1 rounded-full bg-gray-900/70">Parser: {result.parser_used}</span>}
                {result.merchant && <span className="px-2 py-1 rounded-full bg-gray-900/70">Merchant: {result.merchant}</span>}
                {result.merchant_type && <span className="px-2 py-1 rounded-full bg-gray-900/70">Type: {result.merchant_type}</span>}
              </div>
            </div>

            <div className="overflow-x-auto rounded-lg border border-gray-800">
              <table className="w-full text-sm">
                <thead className="bg-green-700 text-white">
                  <tr>
                    <th className="px-4 py-3 text-left">Item</th>
                    <th className="px-4 py-3 text-left">Category</th>
                    <th className="px-4 py-3 text-left">Matched</th>
                    <th className="px-4 py-3 text-left">Score</th>
                    <th className="px-4 py-3 text-left">Qty</th>
                    <th className="px-4 py-3 text-left">kg CO₂</th>
                  </tr>
                </thead>
                <tbody>
                  {result.items.map((it, idx) => {
                    if (!it) return null;
                    const isTop3 = result.items
                      .slice()
                      .sort((a, b) => b.footprint - a.footprint)
                      .slice(0, 3)
                      .some((t) => t && t.name === it.name);
                    return (
                      <tr
                        key={idx}
                        className={`border-b border-gray-800 ${isTop3 ? "bg-green-900/20 font-medium" : "bg-gray-900/50"}`}
                      >
                        <td className="px-4 py-2 text-white">{it.name}</td>
                        <td className="px-4 py-2">
                          <Badge>{it.category || "food"}</Badge>
                        </td>
                        <td className="px-4 py-2 text-gray-300">{it.matched_name || "No match"}</td>
                        <td className="px-4 py-2">
                          {it.match_score ? (
                            <Badge
                              variant={it.match_score >= 80 ? "success" : it.match_score >= 60 ? "warning" : "danger"}
                            >
                              {it.match_score}%
                            </Badge>
                          ) : (
                            <span className="text-gray-500">N/A</span>
                          )}
                        </td>
                        <td className="px-4 py-2 text-gray-300">
                          {it.qty} {it.unit}
                        </td>
                        <td className="px-4 py-2 text-white font-medium">{it.footprint}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </Card>

          <Card>
            <h2 className="text-xl font-bold mb-2">Visual Representation</h2>
            <p className="text-sm text-gray-400 mb-4">
              Each bar shows the estimated CO₂ footprint of an item. Colors indicate categories.
            </p>
            <div className="bg-gray-800/50 rounded-lg p-4">
              <canvas ref={canvasRef} style={{ minHeight: 350 }} className="w-full" />
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
