import { useState } from "react";
import axios from "axios";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post("http://localhost:8000/auth/login", { username, password });
      if (res.data && res.data.access_token) {
        localStorage.setItem("token", res.data.access_token);
        alert("Logged in!");
      } else {
        alert("Login failed: No access token received");
      }
    } catch (err) {
      alert("Error: " + (err.response?.data?.detail || err.message));
    }
  };

  return (
    <form onSubmit={handleLogin} className="p-4">
      <h2 className="text-xl mb-2">Login</h2>
      <input className="border p-2 m-2" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
      <input type="password" className="border p-2 m-2" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
      <button type="submit" className="bg-blue-600 text-white p-2 rounded">Login</button>
    </form>
  );
}
