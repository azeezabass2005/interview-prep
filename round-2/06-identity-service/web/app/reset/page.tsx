"use client";

import { useState } from "react";
import { api, ApiError } from "@/lib/api";

export default function Reset() {
  const token = typeof window === "undefined" ? null : new URLSearchParams(window.location.search).get("token");
  const [value, setValue] = useState("");
  const [message, setMessage] = useState<string | null>(null);

  const submit = async () => {
    try {
      if (token) {
        await api("/password-reset/confirm", { method: "POST", body: JSON.stringify({ token, password: value }) });
        setMessage("Password changed. You can sign in now.");
      } else {
        const r = await api<{ message: string }>("/password-reset", { method: "POST", body: JSON.stringify({ email: value }) });
        setMessage(r.message);
      }
    } catch (e) {
      setMessage((e as ApiError).message);
    }
  };

  return (
    <>
      <h1>{token ? "Choose a new password" : "Reset your password"}</h1>
      {message && <p>{message}</p>}
      <p><input type={token ? "password" : "email"} placeholder={token ? "New password" : "Email"} value={value} onChange={(e) => setValue(e.target.value)} /></p>
      <button onClick={submit}>{token ? "Set password" : "Send reset link"}</button>
    </>
  );
}
