"use client";

import { useState } from "react";
import { api, ApiError } from "@/lib/api";

const ENDPOINTS = ["/v1/quotes/AAPL", "/v1/orders", "/v1/accounts/me", "/v1/fx/EURUSD"];

export default function Portal() {
  const [token, setToken] = useState("");
  const [path, setPath] = useState(ENDPOINTS[0]);
  const [result, setResult] = useState<string>("");

  const tryIt = async () => {
    localStorage.setItem("token", token.trim());
    const started = performance.now();
    try {
      const body = await api<unknown>(path);
      setResult(`200 in ${Math.round(performance.now() - started)} ms\n${JSON.stringify(body, null, 2)}`);
    } catch (e) {
      const err = e as ApiError;
      setResult(`${err.status} ${err.code}: ${err.message}\nrequest id: ${err.requestId ?? "?"}`);
    }
  };

  return (
    <>
      <h1>Developer portal</h1>
      <p>Your API token: <input value={token} onChange={(e) => setToken(e.target.value)} style={{ width: 360 }} /></p>
      <p>
        <select value={path} onChange={(e) => setPath(e.target.value)}>{ENDPOINTS.map((p) => <option key={p}>{p}</option>)}</select>{" "}
        <button onClick={tryIt}>Send GET</button>
      </p>
      <pre style={{ background: "var(--panel)", padding: 12 }}>{result}</pre>
      <p>Limits: 100 requests per rolling minute. Retries of failed upstream calls are automatic for safe requests; send an
      <code> Idempotency-Key</code> header on POSTs you want retried.</p>
    </>
  );
}
