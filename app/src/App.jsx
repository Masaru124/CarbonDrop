import { lazy, Suspense } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";
import DashboardLayout from "./layouts/DashboardLayout";
import Spinner from "./ui/Spinner";

const Landing = lazy(() => import("./pages/Landing"));
const LoginPage = lazy(() => import("./pages/Login"));
const RegisterPage = lazy(() => import("./pages/Register"));
const DashboardPage = lazy(() => import("./pages/Dashboard"));
const HistoryPage = lazy(() => import("./pages/History"));
const InsightsPage = lazy(() => import("./pages/Insights"));
const UploadPage = lazy(() => import("./pages/Home"));
const SimulatorPage = lazy(() => import("./pages/Simulator"));
const LeaderboardPage = lazy(() => import("./pages/Leaderboard"));

function Loader() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-950">
      <Spinner size="lg" />
    </div>
  );
}

function DashboardRoute({ children }) {
  return (
    <ProtectedRoute>
      <DashboardLayout>{children}</DashboardLayout>
    </ProtectedRoute>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<Loader />}>
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Protected routes — wrapped in DashboardLayout */}
          <Route
            path="/upload"
            element={
              <DashboardRoute>
                <UploadPage />
              </DashboardRoute>
            }
          />
          <Route
            path="/dashboard"
            element={
              <DashboardRoute>
                <DashboardPage />
              </DashboardRoute>
            }
          />
          <Route
            path="/history"
            element={
              <DashboardRoute>
                <HistoryPage />
              </DashboardRoute>
            }
          />
          <Route
            path="/insights"
            element={
              <DashboardRoute>
                <InsightsPage />
              </DashboardRoute>
            }
          />
          <Route
            path="/simulator"
            element={
              <DashboardRoute>
                <SimulatorPage />
              </DashboardRoute>
            }
          />
          <Route
            path="/leaderboard"
            element={
              <DashboardRoute>
                <LeaderboardPage />
              </DashboardRoute>
            }
          />

          {/* Legacy redirects */}
          <Route path="/carbon-insights" element={<Navigate to="/insights" replace />} />

          {/* Catch-all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
