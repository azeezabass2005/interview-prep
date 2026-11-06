"use client";

import { useEffect, useState } from "react";
import TokenBox from "@/components/TokenBox";
import { api, ApiError } from "@/lib/api";

type Report = { id: string; title: string; sector: string; summary: string; published_at: string };
type Page = { items: Report[]; page: number; page_size: number; has_more: boolean };

const SECTORS = ["", "energy", "tech", "rates", "fx", "credit"];

export default function ReportsPage() {
  const [sector, setSector] = useState("");
  const [page, setPage] = useState(1);
  const [data, setData] = useState<Page | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const qs = new URLSearchParams({ page: String(page), page_size: "20" });
    if (sector) qs.set("sector", sector);
    api<Page>(`/reports?${qs}`)
      .then((p) => {
        setData(p);
        setError(null);
      })
      .catch((e: ApiError) => setError(`${e.message} (request ${e.requestId ?? "?"})`));
  }, [sector, page]);

  return (
    <>
      <TokenBox />
      <h1>Research</h1>
      <select value={sector} onChange={(e) => { setSector(e.target.value); setPage(1); }}>
        {SECTORS.map((s) => (
          <option key={s} value={s}>{s || "All sectors"}</option>
        ))}
      </select>
      {error && <p className="error">{error}</p>}
      <table>
        <thead>
          <tr><th>Published</th><th>Sector</th><th>Title</th><th>Summary</th></tr>
        </thead>
        <tbody>
          {data?.items.map((r) => (
            <tr key={r.id}>
              <td>{r.published_at?.slice(0, 10)}</td>
              <td>{r.sector}</td>
              <td><a href={`/reports/${r.id}`}>{r.title}</a></td>
              <td>{r.summary}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p>
        <button disabled={page === 1} onClick={() => setPage(page - 1)}>Previous</button>{" "}
        Page {page}{" "}
        <button disabled={!data?.has_more} onClick={() => setPage(page + 1)}>Next</button>
      </p>
    </>
  );
}
