"use client";

import { use, useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";

type Doc = { id: string; title: string; content: string; version: number };
type Preview = { title: string; excerpt: string; words: number; version: number };

export default function DocumentPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [doc, setDoc] = useState<Doc | null>(null);
  const [preview, setPreview] = useState<Preview | null>(null);
  const [text, setText] = useState("");
  const [message, setMessage] = useState<string | null>(null);

  const load = () => {
    api<Doc>(`/documents/${id}`).then((d) => { setDoc(d); setText(d.content); }).catch((e: ApiError) => setMessage(e.message));
    api<Preview>(`/documents/${id}/preview`).then(setPreview).catch(() => {});
  };
  useEffect(load, [id]);

  const save = async () => {
    try {
      await api(`/documents/${id}`, { method: "PATCH", body: JSON.stringify({ content: text, version: doc?.version }) });
      setMessage("Saved");
      load();
    } catch (e) {
      setMessage((e as ApiError).message);
    }
  };

  const share = async () => {
    const r = await api<{ token: string; expires_at: string }>(`/documents/${id}/links`, { method: "POST", body: JSON.stringify({ hours: 48 }) });
    setMessage(`Link (expires ${r.expires_at}): ${window.location.origin}/s/${r.token}`);
  };

  if (!doc) return <p>{message ?? "Loading…"}</p>;
  return (
    <>
      <h1>{doc.title} <small>v{doc.version}</small></h1>
      {message && <p>{message}</p>}
      <textarea value={text} onChange={(e) => setText(e.target.value)} rows={16} style={{ width: "100%" }} />
      <p><button onClick={save}>Save</button> <button onClick={share}>Create 48-hour link</button></p>
      {preview && <aside><h2>Preview (v{preview.version}, {preview.words} words)</h2><p>{preview.excerpt}</p></aside>}
    </>
  );
}
