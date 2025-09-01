import { Link, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";

export function Navbar() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");
    setIsLoggedIn(!!token);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    setIsLoggedIn(false);
    navigate("/login");
  };

  return (
    <nav className="bg-green-600 text-white p-4 flex gap-6 items-center">
      <Link to="/" className="hover:underline">
        Upload
      </Link>
      <Link to="/history" className="hover:underline">
        History
      </Link>
      <Link to="/dashboard" className="hover:underline">
        Dashboard
      </Link>
      <Link to="/simulator" className="hover:underline">
        What-if Simulator
      </Link>
      <Link to="/leaderboard" className="hover:underline">
        Leaderboard
      </Link>
      <div className="ml-auto flex gap-4">
        {isLoggedIn ? (
          <button
            onClick={handleLogout}
            className="bg-red-500 px-3 py-1 rounded hover:bg-red-600"
          >
            Logout
          </button>
        ) : (
          <>
            <Link to="/login" className="hover:underline">
              Login
            </Link>
            <Link to="/register" className="hover:underline">
              Register
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}
