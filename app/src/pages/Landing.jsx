import { Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { Leaf, BarChart3, Zap, TrendingDown, ArrowRight } from "lucide-react";

const features = [
  {
    icon: BarChart3,
    title: "Track Your Footprint",
    description: "Upload receipts and get instant carbon footprint analysis powered by AI.",
  },
  {
    icon: Zap,
    title: "Smart Insights",
    description: "Personalized recommendations to reduce your environmental impact.",
  },
  {
    icon: TrendingDown,
    title: "What-If Simulations",
    description: "See how lifestyle changes affect your carbon footprint before making them.",
  },
  {
    icon: Leaf,
    title: "Gamified Progress",
    description: "Earn eco-credits, plant virtual trees, and compete on the leaderboard.",
  },
];

export default function Landing() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <nav className="flex items-center justify-between px-6 py-4 max-w-7xl mx-auto">
        <div className="flex items-center gap-2 text-xl font-bold text-green-400">
          <Leaf className="h-6 w-6" />
          CarbonTracker
        </div>
        <div className="flex items-center gap-3">
          {isAuthenticated ? (
            <Link
              to="/dashboard"
              className="px-5 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-semibold text-sm transition"
            >
              Dashboard
            </Link>
          ) : (
            <>
              <Link
                to="/login"
                className="px-4 py-2 text-sm text-gray-300 hover:text-white transition"
              >
                Login
              </Link>
              <Link
                to="/register"
                className="px-5 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-semibold text-sm transition"
              >
                Get Started
              </Link>
            </>
          )}
        </div>
      </nav>

      <main>
        <section className="max-w-7xl mx-auto px-6 pt-24 pb-20 text-center">
          <h1 className="text-4xl md:text-6xl font-bold tracking-tight max-w-3xl mx-auto leading-tight">
            Know Your{" "}
            <span className="text-green-400">Carbon Footprint</span>
            , Change Your Impact
          </h1>
          <p className="mt-5 text-lg text-gray-400 max-w-2xl mx-auto leading-relaxed">
            Upload your receipts and let AI analyze your environmental impact.
            Get personalized insights, simulate lifestyle changes, and track your progress toward a sustainable future.
          </p>
          <div className="mt-8 flex items-center justify-center gap-4">
            <Link
              to={isAuthenticated ? "/dashboard" : "/register"}
              className="inline-flex items-center gap-2 px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-xl font-semibold text-base transition shadow-lg shadow-green-600/25"
            >
              {isAuthenticated ? "Go to Dashboard" : "Start Tracking"}
              <ArrowRight className="h-5 w-5" />
            </Link>
          </div>
        </section>

        <section className="max-w-7xl mx-auto px-6 pb-24">
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature) => (
              <div
                key={feature.title}
                className="bg-gray-900 border border-gray-800 rounded-xl p-6 hover:border-gray-700 transition"
              >
                <div className="w-10 h-10 rounded-lg bg-green-600/20 flex items-center justify-center mb-4">
                  <feature.icon className="h-5 w-5 text-green-400" />
                </div>
                <h3 className="font-semibold text-white mb-2">{feature.title}</h3>
                <p className="text-sm text-gray-400 leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="max-w-7xl mx-auto px-6 pb-24">
          <div className="bg-gradient-to-br from-green-700 to-green-900 rounded-2xl p-10 md:p-14 text-center">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Ready to make a difference?
            </h2>
            <p className="text-green-100/80 max-w-lg mx-auto mb-8">
              Join the community of eco-conscious users tracking and reducing their carbon footprint.
            </p>
            <Link
              to={isAuthenticated ? "/dashboard" : "/register"}
              className="inline-flex items-center gap-2 px-6 py-3 bg-white text-green-800 rounded-xl font-semibold text-base hover:bg-green-50 transition"
            >
              {isAuthenticated ? "Go to Dashboard" : "Get Started Free"}
              <ArrowRight className="h-5 w-5" />
            </Link>
          </div>
        </section>
      </main>

      <footer className="border-t border-gray-800 py-8">
        <div className="max-w-7xl mx-auto px-6 text-center text-sm text-gray-500">
          &copy; {new Date().getFullYear()} CarbonTracker. Built with React + Tailwind CSS.
        </div>
      </footer>
    </div>
  );
}
