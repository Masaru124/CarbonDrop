import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { api } from "../lib/api";
import Card from "../ui/Card";
import Button from "../ui/Button";
import Spinner from "../ui/Spinner";
import EmptyState from "../ui/EmptyState";
import Badge from "../ui/Badge";
import { Trophy } from "lucide-react";

export default function LeaderboardPage() {
  const { isAuthenticated } = useAuth();
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated) {
      setLoading(false);
      return;
    }
    api
      .get("/leaderboard")
      .then((d) => setData(Array.isArray(d) ? d : []))
      .catch(() => setData([]))
      .finally(() => setLoading(false));
  }, [isAuthenticated]);

  if (!isAuthenticated) {
    return (
      <div className="p-4 md:p-6 max-w-6xl mx-auto">
        <EmptyState
          icon="🏆"
          title="Community Leaderboard"
          description="Please login to view the leaderboard."
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
    <div className="p-4 md:p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl md:text-3xl font-bold mb-2">Community Leaderboard</h1>
      <p className="text-gray-400 mb-8">Top eco-conscious users by carbon footprint score</p>

      {data.length === 0 ? (
        <EmptyState
          icon="🏆"
          title="No rankings yet"
          description="Be the first to upload receipts and earn your spot!"
          action={<Button onClick={() => navigate("/")}>Upload a Receipt</Button>}
        />
      ) : (
        <div className="space-y-3">
          {data.map((user, i) => (
            <Card key={i} className={`flex items-center gap-4 p-4 ${i === 0 ? "bg-green-900/20 border-green-700" : "bg-gray-900 border-gray-800"}`}>
              <div className="flex-shrink-0 w-8 text-center">
                {i === 0 ? (
                  <Trophy className="h-6 w-6 mx-auto text-green-400" />
                ) : (
                  <span className={`text-lg font-bold ${i < 3 ? "text-green-400" : "text-gray-500"}`}>#{i + 1}</span>
                )}
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-white truncate">{user.username}</p>
              </div>
              <div className="text-right">
                <p className="font-bold text-green-400">{user.score} kg</p>
                <Badge variant={i === 0 ? "success" : "neutral"}>
                  {i === 0 ? "Top Eco" : "Eco Apprentice"}
                </Badge>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
