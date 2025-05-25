import React, { useEffect, useState } from "react";
import { Pie } from "react-chartjs-2";

export default function Dashboard() {
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    fetch("http://localhost:8000/analytics/summary")
      .then(res => res.json())
      .then(setSummary);
  }, []);

  if (!summary) return <div>Loading...</div>;

  const data = {
    labels: ["Creditworthy", "Not Creditworthy"],
    datasets: [{ data: [summary.creditworthy, summary.not_creditworthy], backgroundColor: ["#36A2EB", "#FF6384"] }]
  };

  return (
    <div>
      <h2>Creditworthiness Distribution</h2>
      <Pie data={data} />
      <p>Total Evaluations: {summary.total}</p>
      <p>Creditworthy: {summary.percent_creditworthy.toFixed(1)}%</p>
    </div>
  );
}