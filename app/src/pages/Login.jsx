import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { api } from "../lib/api";
import { useToast } from "../ui/Toast";
import Button from "../ui/Button";
import Input from "../ui/Input";
import Card from "../ui/Card";
import AuthLayout from "../layouts/AuthLayout";
import { Leaf } from "lucide-react";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const { login, isAuthenticated } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) navigate("/dashboard", { replace: true });
  }, [isAuthenticated, navigate]);

  const validate = () => {
    const errs = {};
    if (!username.trim()) errs.username = "Username is required";
    if (!password) errs.password = "Password is required";
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    setLoading(true);
    try {
      const res = await api.post("/auth/login", { username, password });
      login(res.access_token, res.user);
      toast("Welcome back!", "success");
    } catch (err) {
      toast(err.message || "Login failed", "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout>
      <div className="flex flex-col items-center mb-8">
        <Leaf className="h-10 w-10 text-green-400 mb-3" />
        <h1 className="text-2xl font-bold text-white">Welcome back</h1>
        <p className="text-sm text-gray-400 mt-1">Sign in to your CarbonTracker account</p>
      </div>
      <Card className="p-8">
        <form onSubmit={handleLogin} className="space-y-4">
          <Input
            id="username"
            label="Username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Enter your username"
            error={errors.username}
          />
          <Input
            id="password"
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter your password"
            error={errors.password}
          />
          <Button type="submit" loading={loading} className="w-full">
            {loading ? "Signing in..." : "Sign in"}
          </Button>
        </form>

        <p className="text-sm text-gray-400 text-center mt-6">
          Don't have an account?{" "}
          <Link to="/register" className="text-green-400 hover:underline font-medium">
            Create one
          </Link>
        </p>
      </Card>
    </AuthLayout>
  );
}
