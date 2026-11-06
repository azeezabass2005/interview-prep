"use client";

import { useEffect, useState } from "react";

export default function TokenBox() {
  const [token, setToken] = useState("");
  useEffect(() => setToken(window.localStorage.getItem("token") ?? ""), []);
  return (
    <p>
      <input placeholder="Your token" value={token} onChange={(e) => setToken(e.target.value)} style={{ width: 360 }} />{" "}
      <button onClick={() => { window.localStorage.setItem("token", token.trim()); window.location.reload(); }}>Use token</button>{" "}
      <a href="/positions">Positions</a>
    </p>
  );
}
