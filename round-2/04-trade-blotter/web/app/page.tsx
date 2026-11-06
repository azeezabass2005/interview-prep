"use client";

import { useEffect, useState } from "react";
import TokenBox from "@/components/TokenBox";
import { api, ApiError, money } from "@/lib/api";

type Trade = { id: string; symbol: string; side: string; quantity: number; price_cents: number; status: string; counterparty: string; trader_id: string; booked_at: string; version: number };

export default function Blotter() {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({ symbol: "UST10Y", side: "buy", quantity: "100", price_cents: "9850", counterparty_id: "cp_gs" });

  const load = () => api<{ trades: Trade[] }>("/blotter").then((r) => setTrades(r.trades)).catch((e: ApiError) => setError(e.message));
  useEffect(() => { load(); }, []);

  const book = async () => {
    try {
      await api("/trades", { method: "POST", body: JSON.stringify({ ...form, quantity: Number(form.quantity), price_cents: Number(form.price_cents) }) });
      setError(null);
      load();
    } catch (e) {
      setError((e as ApiError).message);
    }
  };

  const amend = async (t: Trade) => {
    const quantity = window.prompt(`New quantity for ${t.id}`, String(t.quantity));
    if (quantity === null) return;
    try {
      await api(`/trades/${t.id}`, { method: "PATCH", body: JSON.stringify({ quantity: Number(quantity) }) });
      load();
    } catch (e) {
      setError((e as ApiError).status >= 500 ? "Something went wrong" : (e as ApiError).message);
    }
  };

  return (
    <>
      <TokenBox />
      <h1>Today&apos;s blotter</h1>
      {error && <p className="error">{error}</p>}
      <p>
        {(["symbol", "quantity", "price_cents", "counterparty_id"] as const).map((k) => (
          <input key={k} placeholder={k} value={form[k]} onChange={(e) => setForm({ ...form, [k]: e.target.value })} style={{ width: 120, marginRight: 6 }} />
        ))}
        <select value={form.side} onChange={(e) => setForm({ ...form, side: e.target.value })}><option>buy</option><option>sell</option></select>{" "}
        <button onClick={book}>Book</button>
      </p>
      <table>
        <thead><tr><th>Time</th><th>Trader</th><th>Side</th><th>Qty</th><th>Symbol</th><th>Price</th><th>Counterparty</th><th>Status</th><th /></tr></thead>
        <tbody>
          {trades.map((t) => (
            <tr key={t.id}>
              <td>{t.booked_at.slice(11)}</td><td>{t.trader_id}</td><td>{t.side}</td><td>{t.quantity}</td><td>{t.symbol}</td>
              <td>{money(t.price_cents)}</td><td>{t.counterparty}</td><td>{t.status} v{t.version}</td>
              <td>{t.status === "live" && <button onClick={() => amend(t)}>Amend</button>}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
}
