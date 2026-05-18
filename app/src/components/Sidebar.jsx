import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import {
  LayoutDashboard,
  History,
  Brain,
  FlaskConical,
  Trophy,
  Upload,
  LogOut,
  Leaf,
} from "lucide-react";

const links = [
  { to: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/upload", icon: Upload, label: "Upload Receipt" },
  { to: "/history", icon: History, label: "History" },
  { to: "/insights", icon: Brain, label: "Insights" },
  { to: "/simulator", icon: FlaskConical, label: "Simulator" },
  { to: "/leaderboard", icon: Trophy, label: "Leaderboard" },
];

export default function Sidebar() {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <aside className="w-64 h-screen bg-gray-950 border-r border-gray-800 flex flex-col flex-shrink-0">
      <div className="p-5 border-b border-gray-800">
        <NavLink to="/dashboard" className="flex items-center gap-2 text-lg font-bold text-green-400">
          <Leaf className="h-6 w-6" />
          CarbonTracker
        </NavLink>
      </div>

      <nav className="flex-1 p-3 space-y-1">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition ${
                isActive
                  ? "bg-green-600/20 text-green-400"
                  : "text-gray-400 hover:text-white hover:bg-gray-800"
              }`
            }
          >
            <link.icon className="h-5 w-5 flex-shrink-0" />
            {link.label}
          </NavLink>
        ))}
      </nav>

      <div className="p-3 border-t border-gray-800">
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-400 hover:text-red-400 hover:bg-red-900/20 transition w-full"
        >
          <LogOut className="h-5 w-5 flex-shrink-0" />
          Logout
        </button>
      </div>
    </aside>
  );
}
