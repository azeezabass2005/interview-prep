"use client";

import { use, useEffect, useState } from "react";
import { api, ApiError, money } from "@/lib/api";

type Expense = { id: string; spent_on: string; merchant: string; category: string; amount_minor: number; currency: string; usd_cents: number; receipt_status: string; receipt_total: string | null };
type Detail = { id: string; title: string; status: string; expenses: Expense[]; total_usd_cents: number };

export default function ReportPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [report, setReport] = useState<Detail | null>(null);
  const [form, setForm] = useState({ spent_on: "", merchant: "", category: "meals", amount: "", currency: "USD" });
  const [message, setMessage] = useState<string | null>(null);
  const load = () => api<Detail>(`/reports/${id}`).then(setReport).catch((e: ApiError) => setMessage(e.message));
  useEffect(() => { load(); }, [id]);

  const run = (p: Promise<unknown>) => p.then(() => { setMessage(null); load(); }).catch((e: ApiError) => setMessage(e.message));
  const add = () => {
    const minor = Math.round(Number(form.amount) * (form.currency === "JPY" ? 1 : 100));
    run(api(`/reports/${id}/expenses`, { method: "POST", body: JSON.stringify({ ...form, amount_minor: minor }) }));
  };
  const upload = async (e: Expense, file: File) => {
    const b64 = btoa(String.fromCharCode(...new Uint8Array(await file.arrayBuffer())));
    run(api(`/expenses/${e.id}/receipt`, { method: "POST", body: JSON.stringify({ image: b64 }) }));
  };

  if (!report) return <p>{message ?? "Loading…"}</p>;
  const draft = report.status === "draft";
  return (
    <>
      <h1>{report.title} · {report.status}</h1>
      {message && <p className="error">{message}</p>}
      <table>
        <thead><tr><th>Date</th><th>Merchant</th><th>Category</th><th>Amount</th><th>USD</th><th>Receipt</th><th /></tr></thead>
        <tbody>
          {report.expenses.map((e) => (
            <tr key={e.id}>
              <td>{e.spent_on}</td><td>{e.merchant}</td><td>{e.category}</td><td>{e.amount_minor} {e.currency} (minor units)</td>
              <td>{money(e.usd_cents)}</td>
              <td>{e.receipt_status === "done" ? `reads ${e.receipt_total}` : e.receipt_status === "none" ? (draft ? <input type="file" onChange={(ev) => ev.target.files && upload(e, ev.target.files[0])} /> : "none") : e.receipt_status}</td>
              <td>{draft && <button onClick={() => run(api(`/expenses/${e.id}`, { method: "DELETE" }))}>Delete</button>}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p><b>Total: {money(report.total_usd_cents)}</b></p>
      {draft && (
        <>
          <p>
            <input type="date" value={form.spent_on} onChange={(e) => setForm({ ...form, spent_on: e.target.value })} />{" "}
            <input placeholder="Merchant" value={form.merchant} onChange={(e) => setForm({ ...form, merchant: e.target.value })} />{" "}
            <select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>{["travel", "meals", "lodging", "software", "other"].map((c) => <option key={c}>{c}</option>)}</select>{" "}
            <input placeholder="Amount" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} style={{ width: 90 }} />{" "}
            <select value={form.currency} onChange={(e) => setForm({ ...form, currency: e.target.value })}>{["USD", "EUR", "GBP", "JPY"].map((c) => <option key={c}>{c}</option>)}</select>{" "}
            <button onClick={add}>Add expense</button>
          </p>
          <button onClick={() => run(api(`/reports/${id}/submit`, { method: "POST" }))}>Submit for approval</button>
        </>
      )}
    </>
  );
}
