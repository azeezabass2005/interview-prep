"use client";

import { useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";

type Report = { id: string; title: string; employee_id: string; submitted_at: string };

export default function Team() {
  const [reports, setReports] = useState<Report[]>([]);
  const [error, setError] = useState<string | null>(null);
  const load = () => api<{ reports: Report[] }>("/team/reports").then((r) => setReports(r.reports)).catch((e: ApiError) => setError(e.message));
  useEffect(() => { load(); }, []);
  const decide = (id: string, action: "approve" | "reject") => api(`/reports/${id}/${action}`, { method: "POST" }).then(load).catch((e: ApiError) => setError(e.message));
  return (
    <>
      <h1>Waiting for my approval</h1>
      {error && <p className="error">{error}</p>}
      <table>
        <thead><tr><th>Employee</th><th>Report</th><th>Submitted</th><th /></tr></thead>
        <tbody>
          {reports.map((r) => (
            <tr key={r.id}>
              <td>{r.employee_id}</td><td><a href={`/reports/${r.id}`}>{r.title}</a></td><td>{r.submitted_at.slice(0, 10)}</td>
              <td><button onClick={() => decide(r.id, "approve")}>Approve</button> <button onClick={() => decide(r.id, "reject")}>Reject</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
}
