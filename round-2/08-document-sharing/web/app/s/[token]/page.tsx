import { headers } from "next/headers";

export default async function SharedDocument({ params }: { params: Promise<{ token: string }> }) {
  const { token } = await params;
  const host = (await headers()).get("host");
  const res = await fetch(`http://${host}/api/s/${token}`, { cache: "no-store" });
  if (!res.ok) return <p className="error">This link doesn&apos;t exist, has expired or has been turned off.</p>;
  const doc = await res.json();
  return (
    <article>
      <h1>{doc.title}</h1>
      <p style={{ whiteSpace: "pre-wrap" }}>{doc.content}</p>
    </article>
  );
}
