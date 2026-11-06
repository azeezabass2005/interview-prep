"use client";

import { use, useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";

type Report = { id: string; title: string; sector: string; summary: string; body: string; published_at: string };

export default function ReportPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [report, setReport] = useState<Report | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api<Report>(`/reports/${id}`).then(setReport).catch((e: ApiError) => setError(e.message));
  }, [id]);

  if (error) return <p className="error">{error}</p>;
  if (!report) return <p>Loading…</p>;

  // New tabs can't send an Authorization header, so the download link carries the token.
  const pdf = `/api/reports/${id}/pdf?access_token=${encodeURIComponent(localStorage.getItem("token") ?? "")}`;
  return (
    <article>
      <p>{report.sector} · {report.published_at?.slice(0, 10)}</p>
      <h1>{report.title}</h1>
      <p><b>{report.summary}</b></p>
      <p style={{ whiteSpace: "pre-wrap" }}>{report.body}</p>
      <a href={pdf} target="_blank" rel="noreferrer">Download PDF</a>
    </article>
  );
}
