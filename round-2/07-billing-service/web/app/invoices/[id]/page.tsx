"use client";

import { use, useEffect, useState } from "react";
import { api, ApiError, money } from "@/lib/api";

type Detail = {
  period: string; status: string; subtotal_cents: number; tax_cents: number; total_cents: number;
  lines: { description: string; amount_cents: number }[];
  payments: { id: string; amount_cents: number; received_at: string }[];
};

export default function InvoicePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [inv, setInv] = useState<Detail | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => { api<Detail>(`/invoices/${id}`).then(setInv).catch((e: ApiError) => setError(e.message)); }, [id]);
  if (error) return <p className="error">{error}</p>;
  if (!inv) return <p>Loading…</p>;
  return (
    <>
      <h1>Invoice {inv.period} · {inv.status}</h1>
      <table>
        <tbody>
          {inv.lines.map((l, i) => <tr key={i}><td>{l.description}</td><td>{money(l.amount_cents)}</td></tr>)}
          <tr><th>Subtotal</th><th>{money(inv.subtotal_cents)}</th></tr>
          <tr><th>Tax</th><th>{money(inv.tax_cents)}</th></tr>
          <tr><th>Total</th><th>{money(inv.total_cents)}</th></tr>
        </tbody>
      </table>
      <h2>Payments</h2>
      <ul>{inv.payments.map((p) => <li key={p.id}>{money(p.amount_cents)} on {p.received_at.slice(0, 10)}</li>)}</ul>
    </>
  );
}
