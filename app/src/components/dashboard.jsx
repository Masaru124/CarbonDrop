import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Line } from "react-chartjs-2";

export default function Dashboard() {
  const [data, setData] = useState([]);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");
    setIsLoggedIn(!!token);
    if (token) {
      fetch("http://localhost:8000/dashboard", {
        headers: { "Authorization": `Bearer ${token}` }
      })
        .then((res) => res.json())
        .then((data) => {
          if (Array.isArray(data)) {
            setData(data);
          } else {
            setData([]);
            console.error("Dashboard data is not an array:", data);
          }
        });
    }
  }, []);

  const downloadReport = () => {
    const token = localStorage.getItem("token");
    if (!token) return;
    fetch("http://localhost:8000/report/pdf", {
      headers: { "Authorization": `Bearer ${token}` }
    })
      .then(res => res.blob())
      .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'footprint_report.pdf';
        a.click();
      });
  };

  if (!isLoggedIn) {
    return (
      <div className="p-6">
        <h1 className="text-2xl font-bold">My Carbon Dashboard</h1>
        <div className="text-center">
          <p className="text-lg mb-4">Please login to view your carbon footprint dashboard.</p>
          <button
            onClick={() => navigate("/login")}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition"
          >
            Go to Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold">My Carbon Dashboard</h1>
      <button onClick={downloadReport} className="mb-4 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">Download PDF Report</button>
      <Line
        data={{
          labels: data.map((d) => d.month),
          datasets: [
            {
              label: "kg CO₂e",
              data: data.map((d) => d.total),
              borderColor: "green",
            },
          ],
        }}
      />
    </div>
  );
}
