import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import { useToast } from "../ui/Toast";
import Button from "../ui/Button";
import Input from "../ui/Input";
import Card from "../ui/Card";
import AuthLayout from "../layouts/AuthLayout";
import { Leaf } from "lucide-react";

export default function RegisterPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const toast = useToast();
  const navigate = useNavigate();

  const validate = () => {
    const errs = {};
    if (!username.trim()) errs.username = "Username is required";
    if (!password) errs.password = "Password is required";
    else if (password.length < 6) errs.password = "Must be at least 6 characters";
    if (password !== confirmPassword) errs.confirmPassword = "Passwords do not match";
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    setLoading(true);
    try {
      await api.post("/auth/register", { username, password });
      toast("Registration successful! Please sign in.", "success");
      navigate("/login");
    } catch (err) {
      toast(err.message || "Registration failed", "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout>
      <div className="flex flex-col items-center mb-8">
        <Leaf className="h-10 w-10 text-green-400 mb-3" />
        <h1 className="text-2xl font-bold text-white">Create your account</h1>
        <p className="text-sm text-gray-400 mt-1">Start tracking your carbon footprint</p>
      </div>
      <Card className="p-8">
        <form onSubmit={handleRegister} className="space-y-4">
          <Input
            id="reg-username"
            label="Username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Choose a username"
            error={errors.username}
          />
          <Input
            id="reg-password"
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Create a password"
            error={errors.password}
          />
          <Input
            id="reg-confirm"
            label="Confirm Password"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="Confirm your password"
            error={errors.confirmPassword}
          />
          <Button type="submit" loading={loading} className="w-full">
            {loading ? "Creating account..." : "Create account"}
          </Button>
        </form>

        <p className="text-sm text-gray-400 text-center mt-6">
          Already have an account?{" "}
          <Link to="/login" className="text-green-400 hover:underline font-medium">
            Sign in
          </Link>
        </p>
      </Card>
    </AuthLayout>
  );
}
