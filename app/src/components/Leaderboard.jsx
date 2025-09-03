import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Leaderboard() {
  const [data, setData] = useState([]);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");
    setIsLoggedIn(!!token);
    if (token) {
      fetch("http://localhost:8000/leaderboard", {
        headers: { "Authorization": `Bearer ${token}` }
      })
        .then((res) => res.json())
        .then((data) => {
          if (Array.isArray(data)) {
            setData(data);
          } else {
            setData([]);
            console.error("Leaderboard data is not an array:", data);
          }
        });
    }
  }, []);

  if (!isLoggedIn) {
    return (
      <div className="p-6 mx-auto max-w-6xl text-white">
        <h1 className="text-2xl font-bold">Community Leaderboard</h1>
        <div className="text-center">
          <p className="text-lg mb-4">Please login to view the community leaderboard.</p>
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
    <div className="p-6 mx-auto text-white h-[80vh]">
      <h1 className="text-2xl font-bold">Community Leaderboard</h1>
      <ul>
        {data.map((u, i) => (
          <li key={i} className="py-2 border-b border-gray-700">
            {u.username} — {u.score} kg CO₂e
          </li>
        ))}
      </ul>
    </div>
  );
}
