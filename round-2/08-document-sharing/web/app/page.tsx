"use client";

import { useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";

type Doc = { id: string; title: string; owner_id: string; version: number; updated_at: string };

export default function Documents() {
  const [token, setToken] = useState("");
  const [docs, setDocs] = useState<Doc[]>([]);
  const [cursor, setCursor] = useState<string | null>(null);
  const [q, setQ] = useState("");
  const [error, setError] = useState<string | null>(null);

  const load = (next?: string) =>
    api<{ documents: Doc[]; next_cursor: string | null }>(`/documents${next ? `?cursor=${next}` : ""}`)
      .then((r) => { setDocs((d) => (next ? [...d, ...r.documents] : r.documents)); setCursor(r.next_cursor); })
      .catch((e: ApiError) => setError(e.message));

  useEffect(() => { setToken(localStorage.getItem("token") ?? ""); load(); }, []);

  const search = () =>
    q.trim().length < 2 ? load() : api<{ documents: Doc[] }>(`/search?q=${encodeURIComponent(q)}`).then((r) => { setDocs(r.documents); setCursor(null); });

  const create = async () => {
    const title = window.prompt("Title");
    if (!title) return;
    await api("/documents", { method: "POST", body: JSON.stringify({ title, content: "" }) });
    load();
  };

  return (
    <>
      <p>
        <input placeholder="Your token" value={token} onChange={(e) => setToken(e.target.value)} style={{ width: 360 }} />{" "}
        <button onClick={() => { localStorage.setItem("token", token.trim()); load(); }}>Use token</button>
      </p>
      {error && <p className="error">{error}</p>}
      <h1>Documents</h1>
      <p>
        <input placeholder="Search titles" value={q} onChange={(e) => setQ(e.target.value)} /> <button onClick={search}>Search</button>{" "}
        <button onClick={create}>New document</button>
      </p>
      <table>
        <thead><tr><th>Title</th><th>Owner</th><th>Version</th><th>Updated</th></tr></thead>
        <tbody>{docs.map((d) => <tr key={d.id}><td><a href={`/documents/${d.id}`}>{d.title}</a></td><td>{d.owner_id}</td><td>{d.version}</td><td>{d.updated_at.replace("T", " ")}</td></tr>)}</tbody>
      </table>
      {cursor && <button onClick={() => load(cursor)}>Load more</button>}
    </>
  );
}
