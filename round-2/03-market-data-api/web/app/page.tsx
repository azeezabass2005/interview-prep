"use client";

import { useEffect, useState } from "react";
import TokenBox from "@/components/TokenBox";
import { api, ApiError } from "@/lib/api";

type Instrument = { symbol: string; name: string; exchange: string; currency: string };
type Quote = { symbol: string; price: number; currency: string; as_of: string };

export default function Home() {
  const [q, setQ] = useState("");
  const [results, setResults] = useState<Instrument[]>([]);
  const [watch, setWatch] = useState<Quote[]>([]);
  const [ccy, setCcy] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (q.trim().length < 2) return setResults([]);
    api<{ instruments: Instrument[] }>(`/instruments?q=${encodeURIComponent(q)}`)
      .then((r) => setResults(r.instruments))
      .catch((e: ApiError) => setError(e.message));
  }, [q]);

  useEffect(() => {
    const tick = () =>
      api<{ quotes: Quote[] }>(`/quotes?symbols=AAPL,MSFT,VOD,SAP${ccy ? `&ccy=${ccy}` : ""}`)
        .then((r) => setWatch(r.quotes))
        .catch((e: ApiError) => setError(e.message));
    tick();
    const id = setInterval(tick, 2000);
    return () => clearInterval(id);
  }, [ccy]);

  return (
    <>
      <TokenBox />
      {error && <p className="error">{error}</p>}
      <h1>Watchlist</h1>
      <select value={ccy} onChange={(e) => setCcy(e.target.value)}>
        {["", "USD", "EUR", "GBP"].map((c) => <option key={c} value={c}>{c || "Local currency"}</option>)}
      </select>
      <table>
        <thead><tr><th>Symbol</th><th>Price</th><th>As of</th></tr></thead>
        <tbody>{watch.map((w) => <tr key={w.symbol}><td>{w.symbol}</td><td>{w.price} {w.currency}</td><td>{w.as_of}</td></tr>)}</tbody>
      </table>
      <h2>Search</h2>
      <input placeholder="Name or symbol" value={q} onChange={(e) => setQ(e.target.value)} />
      <ul>{results.map((i) => <li key={i.symbol}><a href={`/instruments/${i.symbol}`}>{i.symbol}</a> {i.name} ({i.exchange})</li>)}</ul>
    </>
  );
}
