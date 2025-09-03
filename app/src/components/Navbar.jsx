import { Link, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { Menu, X } from "lucide-react"; // icons for mobile toggle

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
    <nav className="bg-green-600 text-white p-4 flex items-center justify-between">
      {/* Logo / Brand */}
      <Link to="/" className="font-bold text-lg">
        CarbonTracker
      </Link>

      {/* Desktop Menu */}
      <div className="hidden md:flex gap-6">
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
      </div>

      {/* Auth Buttons (Desktop) */}
      <div className="hidden md:flex gap-4 ml-auto">
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

      {/* Mobile Hamburger */}
      <button className="md:hidden p-2" onClick={() => setMenuOpen(!menuOpen)}>
        {menuOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      {/* Mobile Dropdown Menu */}
      {menuOpen && (
        <div className="absolute top-16 left-0 w-full bg-green-700 p-4 flex flex-col gap-4 md:hidden shadow-lg z-50">
          <Link
            to="/"
            className="hover:underline"
            onClick={() => setMenuOpen(false)}
          >
            Upload
          </Link>
          <Link
            to="/history"
            className="hover:underline"
            onClick={() => setMenuOpen(false)}
          >
            History
          </Link>
          <Link
            to="/dashboard"
            className="hover:underline"
            onClick={() => setMenuOpen(false)}
          >
            Dashboard
          </Link>
          <Link
            to="/simulator"
            className="hover:underline"
            onClick={() => setMenuOpen(false)}
          >
            What-if Simulator
          </Link>
          <Link
            to="/leaderboard"
            className="hover:underline"
            onClick={() => setMenuOpen(false)}
          >
            Leaderboard
          </Link>

          <div className="border-t border-green-500 pt-4">
            {isLoggedIn ? (
              <button
                onClick={() => {
                  handleLogout();
                  setMenuOpen(false);
                }}
                className="bg-red-500 px-3 py-1 rounded hover:bg-red-600 w-full text-left"
              >
                Logout
              </button>
            ) : (
              <>
                <Link
                  to="/login"
                  className="hover:underline block"
                  onClick={() => setMenuOpen(false)}
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  className="hover:underline block"
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
