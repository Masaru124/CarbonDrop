import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { api } from "../lib/api";
import Card from "../ui/Card";
import Button from "../ui/Button";
import Spinner from "../ui/Spinner";
import EmptyState from "../ui/EmptyState";
import Badge from "../ui/Badge";

export default function HistoryPage() {
  const { isAuthenticated } = useAuth();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated) {
      setLoading(false);
      return;
    }
    api
      .get("/footprint_history")
      .then((d) => setHistory(d || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [isAuthenticated]);

  if (!isAuthenticated) {
    return (
      <div className="p-4 md:p-6 max-w-6xl mx-auto">
        <EmptyState
          icon="📜"
          title="History"
          description="Please login to view your receipt history."
          action={<Button onClick={() => navigate("/login")}>Go to Login</Button>}
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

  return (
    <div className="p-4 md:p-6 max-w-6xl mx-auto">
      <h1 className="text-2xl md:text-3xl font-bold mb-6">History</h1>

      {history.length === 0 ? (
        <EmptyState
          icon="📭"
          title="No history yet"
          description="Upload your first receipt to get started."
          action={
            <Button onClick={() => navigate("/upload")}>Upload a Receipt</Button>
          }
        />
      ) : (
        <div className="space-y-3">
          {history.map((h) => (
            <Card key={h.id} className="p-4 hover:bg-gray-800/50 transition">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                <div>
                  <p className="text-sm text-gray-100 font-medium">
                    {new Date(h.date).toLocaleString()}
                  </p>
                  <div className="flex items-center gap-2 mt-1">
                    <Badge variant="info">
                      {h.document_type?.charAt(0).toUpperCase() + h.document_type?.slice(1)}
                    </Badge>
                    <span className="text-xs text-gray-500">{h.items?.length || 0} items</span>
                  </div>
                </div>
                <span className="text-lg font-semibold text-green-400">
                  {h.total_footprint} kg CO₂
                </span>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
