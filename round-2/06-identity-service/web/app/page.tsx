"use client";

import { useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";

type Me = { email: string; name: string; org_id: string; permissions: string[] };

export default function Account() {
  const [me, setMe] = useState<Me | null>(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => { api<Me>("/me").then(setMe).catch(() => setMe(null)); }, []);

  const login = async () => {
    try {
      const r = await api<{ session_token: string }>("/login", { method: "POST", body: JSON.stringify({ email, password }) });
      localStorage.setItem("token", r.session_token);
      setMe(await api<Me>("/me"));
      setError(null);
    } catch (e) {
      setError((e as ApiError).message);
    }
  };

  if (me)
    return (
      <>
        <h1>Signed in as {me.name}</h1>
        <p>{me.email} · {me.org_id}</p>
        <p>Permissions: {me.permissions.join(", ") || "none"}</p>
        {me.permissions.includes("users:read") && <p><a href="/admin">Manage users</a></p>}
        <button onClick={async () => { await api("/logout", { method: "POST" }); localStorage.removeItem("token"); setMe(null); }}>Sign out</button>
      </>
    );
  return (
    <>
      <h1>Sign in</h1>
      {error && <p className="error">{error}</p>}
      <p><input placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} /></p>
      <p><input placeholder="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} /></p>
      <p><button onClick={login}>Sign in</button> <a href="/reset">Forgot your password?</a></p>
    </>
  );
}
