"use client";

import { useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";

type Report = { id: string; title: string; status: string; submitted_at: string | null };

export default function MyReports() {
  const [token, setToken] = useState("");
  const [reports, setReports] = useState<Report[]>([]);
  const [error, setError] = useState<string | null>(null);
  const load = () => api<{ reports: Report[] }>("/reports").then((r) => setReports(r.reports)).catch((e: ApiError) => setError(e.message));
  useEffect(() => { setToken(localStorage.getItem("token") ?? ""); load(); }, []);

  const create = async () => {
    const title = window.prompt("Report title (e.g. Berlin client visit)");
    if (!title) return;
    const r = await api<Report>("/reports", { method: "POST", body: JSON.stringify({ title }) });
    window.location.href = `/reports/${r.id}`;
  };

  return (
    <>
      <p>
        <input placeholder="Your token" value={token} onChange={(e) => setToken(e.target.value)} style={{ width: 360 }} />{" "}
        <button onClick={() => { localStorage.setItem("token", token.trim()); load(); }}>Use token</button>{" "}
        <a href="/team">Team approvals</a>
      </p>
      {error && <p className="error">{error}</p>}
      <h1>My expense reports</h1>
      <button onClick={create}>New report</button>
      <table>
        <thead><tr><th>Title</th><th>Status</th><th>Submitted</th></tr></thead>
        <tbody>{reports.map((r) => <tr key={r.id}><td><a href={`/reports/${r.id}`}>{r.title}</a></td><td>{r.status}</td><td>{r.submitted_at?.slice(0, 10) ?? ""}</td></tr>)}</tbody>
      </table>
    </>
  );
}
