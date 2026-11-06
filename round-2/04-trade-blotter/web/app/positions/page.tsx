"use client";

import { useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";

export default function Positions() {
  const [data, setData] = useState<{ desk: string; positions: Record<string, number> } | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => { api<{ desk: string; positions: Record<string, number> }>("/positions").then(setData).catch((e: ApiError) => setError(e.message)); }, []);
  if (error) return <p className="error">{error}</p>;
  if (!data) return <p>Loading…</p>;
  return (
    <>
      <h1>{data.desk} positions</h1>
      <table>
        <thead><tr><th>Symbol</th><th>Net quantity</th></tr></thead>
        <tbody>{Object.entries(data.positions).map(([s, q]) => <tr key={s}><td>{s}</td><td>{q}</td></tr>)}</tbody>
      </table>
    </>
  );
}
