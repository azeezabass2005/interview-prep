"use client";

import { useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";

type Delivery = { id: string; channel: string; message: string; status: string; error: string | null; created_at: string; sent_at: string | null };

export default function Deliveries() {
  const [items, setItems] = useState<Delivery[]>([]);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => { api<{ deliveries: Delivery[] }>("/deliveries").then((r) => setItems(r.deliveries)).catch((e: ApiError) => setError(e.message)); }, []);
  return (
    <>
      <h1>Delivery history</h1>
      {error && <p className="error">{error}</p>}
      <table>
        <thead><tr><th>Fired</th><th>Channel</th><th>Message</th><th>Status</th></tr></thead>
        <tbody>{items.map((d) => <tr key={d.id}><td>{d.created_at.replace("T", " ")}</td><td>{d.channel}</td><td>{d.message}</td><td>{d.status}</td></tr>)}</tbody>
      </table>
    </>
  );
}
