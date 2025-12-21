import { Link, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { Menu, X } from "lucide-react";

export function Navbar() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
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
    <nav className="bg-gray-950 border-b border-gray-800 text-white px-6 py-4 flex items-center justify-between shadow-lg sticky top-0 z-50">
      {/* Brand / Logo */}
      <Link to="/" className="text-2xl font-bold text-green-400 tracking-wide">
        🌍 CarbonTracker
      </Link>

      {/* Desktop Menu */}
      <div className="hidden md:flex gap-8 ml-10">
        <Link to="/" className="hover:text-green-400 transition">
          Upload
        </Link>
        <Link to="/history" className="hover:text-green-400 transition">
          History
        </Link>
        <Link to="/dashboard" className="hover:text-green-400 transition">
          Dashboard
        </Link>
        <Link to="/carbon-insights" className="hover:text-green-400 transition">
          Carbon
        </Link>
        <Link to="/simulator" className="hover:text-green-400 transition">
          Simulator
        </Link>
        <Link to="/leaderboard" className="hover:text-green-400 transition">
          Leaderboard
        </Link>
      </div>

      {/* Auth Buttons (Desktop) */}
      <div className="hidden md:flex gap-4 ml-auto">
        {isLoggedIn ? (
          <button
            onClick={handleLogout}
            className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg font-semibold transition"
          >
            Logout
          </button>
        ) : (
          <>
            <Link
              to="/login"
              className="px-4 py-2 rounded-lg font-semibold text-gray-200 hover:text-green-400 transition"
            >
              Login
            </Link>
            <Link
              to="/register"
              className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg font-semibold transition"
            >
              Register
            </Link>
          </>
        )}
      </div>

      {/* Mobile Hamburger */}
      <button
        className="md:hidden p-2 text-gray-200 hover:text-green-400 transition"
        onClick={() => setMenuOpen(!menuOpen)}
      >
        {menuOpen ? <X size={28} /> : <Menu size={28} />}
      </button>

      {/* Mobile Dropdown Menu */}
      {menuOpen && (
        <div className="absolute top-16 left-0 w-full bg-gray-900 border-t border-gray-800 p-6 flex flex-col gap-4 md:hidden shadow-xl z-50">
          <Link
            to="/"
            className="hover:text-green-400 transition"
            onClick={() => setMenuOpen(false)}
          >
            Upload
          </Link>
          <Link
            to="/history"
            className="hover:text-green-400 transition"
            onClick={() => setMenuOpen(false)}
          >
            History
          </Link>
          <Link
            to="/dashboard"
            className="hover:text-green-400 transition"
            onClick={() => setMenuOpen(false)}
          >
            Dashboard
          </Link>
          <Link
            to="/carbon-insights"
            className="hover:text-green-400 transition"
            onClick={() => setMenuOpen(false)}
          >
            Carbon AI
          </Link>
          <Link
            to="/simulator"
            className="hover:text-green-400 transition"
            onClick={() => setMenuOpen(false)}
          >
            Simulator
          </Link>
          <Link
            to="/leaderboard"
            className="hover:text-green-400 transition"
            onClick={() => setMenuOpen(false)}
          >
            Leaderboard
          </Link>

          <div className="border-t border-gray-700 pt-4 mt-2">
            {isLoggedIn ? (
              <button
                onClick={() => {
                  handleLogout();
                  setMenuOpen(false);
                }}
                className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg w-full text-left font-semibold transition"
              >
                Logout
              </button>
            ) : (
              <>
                <Link
                  to="/login"
                  className="block px-4 py-2 rounded-lg hover:text-green-400 transition"
                  onClick={() => setMenuOpen(false)}
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  className="block bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg font-semibold transition mt-2"
                  onClick={() => setMenuOpen(false)}
                >
                  Register
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </nav>
  );
}
