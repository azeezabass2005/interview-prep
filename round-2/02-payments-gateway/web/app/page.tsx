"use client";

import { useEffect, useState } from "react";
import TokenBox from "@/components/TokenBox";
import { api, ApiError } from "@/lib/api";

type Payment = { id: string; amount: string; currency: string; description: string; status: string; failure_code: string | null; created_at: string };

export default function PaymentsPage() {
  const [status, setStatus] = useState("");
  const [items, setItems] = useState<Payment[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api<{ items: Payment[] }>(`/payments${status ? `?status=${status}` : ""}`)
      .then((r) => setItems(r.items))
      .catch((e: ApiError) => setError(e.message));
  }, [status]);

  return (
    <>
      <TokenBox />
      <h1>Payments</h1>
      <select value={status} onChange={(e) => setStatus(e.target.value)}>
        {["", "captured", "pending", "processing", "failed"].map((s) => <option key={s} value={s}>{s || "All"}</option>)}
      </select>
      {error && <p className="error">{error}</p>}
      <table>
        <thead><tr><th>Created</th><th>Amount</th><th>Description</th><th>Status</th></tr></thead>
        <tbody>
          {items.map((p) => (
            <tr key={p.id}>
              <td>{p.created_at.replace("T", " ")}</td>
              <td>{p.amount} {p.currency}</td>
              <td><a href={`/payments/${p.id}`}>{p.description || p.id}</a></td>
              <td>{p.status}{p.failure_code ? ` (${p.failure_code})` : ""}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
}
