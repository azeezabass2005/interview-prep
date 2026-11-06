"use client";

import { useEffect, useState } from "react";
import TokenBox from "@/components/TokenBox";
import { api, ApiError } from "@/lib/api";

type Rule = { id: string; symbol: string; direction: string; threshold: number; channel: string; active: boolean; triggered_at: string | null };

export default function Alerts() {
  const [rules, setRules] = useState<Rule[]>([]);
  const [form, setForm] = useState({ symbol: "AAPL", direction: "above", threshold: "200", channel: "email" });
  const [error, setError] = useState<string | null>(null);

  const load = () => api<{ rules: Rule[] }>("/rules").then((r) => setRules(r.rules)).catch((e: ApiError) => setError(e.message));
  useEffect(() => { load(); }, []);

  const create = async () => {
    try {
      await api("/rules", { method: "POST", body: JSON.stringify({ ...form, threshold: Number(form.threshold) }) });
      setError(null);
      load();
    } catch (e) {
      setError((e as ApiError).message);
    }
  };

  return (
    <>
      <TokenBox />
      <h1>My price alerts</h1>
      {error && <p className="error">{error}</p>}
      <p>
        <input value={form.symbol} onChange={(e) => setForm({ ...form, symbol: e.target.value })} style={{ width: 90 }} />{" "}
        <select value={form.direction} onChange={(e) => setForm({ ...form, direction: e.target.value })}><option>above</option><option>below</option></select>{" "}
        <input value={form.threshold} onChange={(e) => setForm({ ...form, threshold: e.target.value })} style={{ width: 90 }} />{" "}
        <select value={form.channel} onChange={(e) => setForm({ ...form, channel: e.target.value })}><option>email</option><option>sms</option></select>{" "}
        <button onClick={create}>Add alert</button>
      </p>
      <table>
        <thead><tr><th>Symbol</th><th>Condition</th><th>Channel</th><th>Status</th><th /></tr></thead>
        <tbody>
          {rules.map((r) => (
            <tr key={r.id}>
              <td>{r.symbol}</td><td>{r.direction} {r.threshold}</td><td>{r.channel}</td>
              <td>{r.active ? "watching" : `fired ${r.triggered_at?.replace("T", " ")}`}</td>
              <td><button onClick={() => api(`/rules/${r.id}`, { method: "DELETE" }).then(load)}>Delete</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
}
