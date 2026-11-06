"use client";

import { use, useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";

type Bar = { day: string; open: number; high: number; low: number; close: number; volume: number };

export default function History({ params }: { params: Promise<{ symbol: string }> }) {
  const { symbol } = use(params);
  const [bars, setBars] = useState<Bar[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const to = new Date();
    const from = new Date(to.getTime() - 90 * 86400_000);
    const d = (x: Date) => x.toISOString().slice(0, 10);
    api<{ bars: Bar[] }>(`/instruments/${symbol}/history?from=${d(from)}&to=${d(to)}`)
      .then((r) => setBars(r.bars))
      .catch((e: ApiError) => setError(e.message));
  }, [symbol]);

  return (
    <>
      <h1>{symbol}: last 90 days</h1>
      {error && <p className="error">{error}</p>}
      <table>
        <thead><tr><th>Day</th><th>Open</th><th>High</th><th>Low</th><th>Close</th><th>Volume</th></tr></thead>
        <tbody>{bars.map((b) => <tr key={b.day}><td>{b.day}</td><td>{b.open}</td><td>{b.high}</td><td>{b.low}</td><td>{b.close}</td><td>{b.volume}</td></tr>)}</tbody>
      </table>
    </>
  );
}
