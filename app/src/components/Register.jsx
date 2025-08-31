import { useState } from "react";
import axios from "axios";

export default function Register() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post("http://localhost:8000/auth/register", { username, password });
      if (res.data) {
        alert("Registration successful, now login!");
      } else {
        alert("Registration failed: No response data");
      }
    } catch (err) {
      alert("Error: " + (err.response?.data?.detail || err.message));
    }
  };

  return (
    <form onSubmit={handleRegister} className="p-4">
      <h2 className="text-xl mb-2">Register</h2>
      <input className="border p-2 m-2" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
      <input type="password" className="border p-2 m-2" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
      <button type="submit" className="bg-green-600 text-white p-2 rounded">Register</button>
    </form>
  );
}
