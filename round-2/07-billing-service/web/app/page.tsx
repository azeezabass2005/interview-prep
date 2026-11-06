"use client";

import { useEffect, useState } from "react";
import { api, ApiError, money } from "@/lib/api";

type Invoice = { id: string; period: string; subtotal_cents: number; tax_cents: number; total_cents: number; status: string };

export default function Billing() {
  const [token, setToken] = useState("");
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [seats, setSeats] = useState("");
  const [message, setMessage] = useState<string | null>(null);

  const load = () => api<{ invoices: Invoice[] }>("/invoices").then((r) => setInvoices(r.invoices)).catch((e: ApiError) => setMessage(e.message));
  useEffect(() => { setToken(localStorage.getItem("token") ?? ""); load(); }, []);

  const changeSeats = async () => {
    try {
      const r = await api<{ seats: number; prorated_charge_cents: number }>("/seats", { method: "POST", body: JSON.stringify({ seats: Number(seats) }) });
      setMessage(`Now ${r.seats} seats. Charged today: ${money(r.prorated_charge_cents)} (on your next invoice).`);
    } catch (e) {
      setMessage((e as ApiError).message);
    }
  };

  return (
    <>
      <p>
        <input placeholder="Billing admin token" value={token} onChange={(e) => setToken(e.target.value)} style={{ width: 360 }} />{" "}
        <button onClick={() => { localStorage.setItem("token", token.trim()); load(); }}>Use token</button>
      </p>
      {message && <p>{message}</p>}
      <h1>Seats</h1>
      <p><input placeholder="New seat count" value={seats} onChange={(e) => setSeats(e.target.value)} /> <button onClick={changeSeats}>Update seats</button></p>
      <h1>Invoices</h1>
      <table>
        <thead><tr><th>Period</th><th>Subtotal</th><th>Tax</th><th>Total</th><th>Status</th></tr></thead>
        <tbody>
          {invoices.map((i) => (
            <tr key={i.id}>
              <td><a href={`/invoices/${i.id}`}>{i.period}</a></td><td>{money(i.subtotal_cents)}</td><td>{money(i.tax_cents)}</td>
              <td>{money(i.total_cents)}</td><td>{i.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
}
