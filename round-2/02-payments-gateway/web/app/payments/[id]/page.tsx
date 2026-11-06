"use client";

import { use, useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";

type Payment = { id: string; amount: string; currency: string; description: string; status: string; failure_code: string | null };
type Refund = { id: string; amount: string; status: string };

export default function PaymentPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [payment, setPayment] = useState<Payment | null>(null);
  const [refunds, setRefunds] = useState<Refund[]>([]);
  const [amount, setAmount] = useState("");
  const [message, setMessage] = useState<string | null>(null);

  const load = () => {
    api<Payment>(`/payments/${id}`).then(setPayment).catch((e: ApiError) => setMessage(e.message));
    api<{ items: Refund[] }>(`/payments/${id}/refunds`).then((r) => setRefunds(r.items)).catch(() => {});
  };
  useEffect(load, [id]);

  const refund = async () => {
    try {
      await api(`/payments/${id}/refunds`, { method: "POST", body: JSON.stringify(amount ? { amount } : {}) });
      setAmount("");
      load();
    } catch (e) {
      setMessage((e as ApiError).message);
    }
  };

  if (!payment) return <p>{message ?? "Loading…"}</p>;
  return (
    <>
      <h1>{payment.amount} {payment.currency}</h1>
      <p>{payment.description} · {payment.status}{payment.failure_code ? ` (${payment.failure_code})` : ""}</p>
      {message && <p className="error">{message}</p>}
      <h2>Refunds</h2>
      <ul>{refunds.map((r) => <li key={r.id}>{r.amount} {payment.currency} · {r.status}</li>)}</ul>
      {payment.status === "captured" && (
        <p>
          <input placeholder={`Amount (blank = full)`} value={amount} onChange={(e) => setAmount(e.target.value)} />{" "}
          <button onClick={refund}>Refund</button>
        </p>
      )}
    </>
  );
}
