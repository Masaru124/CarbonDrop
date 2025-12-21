import { Navbar } from "./components/Navbar";
import Footer from "./components/Footer";
import History from "./components/History";
import Dashboard from "./components/dashboard";
import Leaderboard from "./components/Leaderboard";
import Upload from "./components/Upload";
import Register from "./components/Register";
import Login from "./components/Login";
import Simulator from "./components/Simulator";
import CarbonInsights from "./components/CarbonInsights";
import { BrowserRouter, Routes, Route } from "react-router-dom";

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Upload />} />
        <Route path="/history" element={<History />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/carbon-insights" element={<CarbonInsights />} />
        <Route path="/simulator" element={<Simulator />} />
        <Route path="/leaderboard" element={<Leaderboard />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
      </Routes>
      {/* <Footer /> */}
    </BrowserRouter>
  );
}
