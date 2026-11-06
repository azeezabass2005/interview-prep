"use client";

import { useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";

type User = { id: string; email: string; name: string; roles: string[] };

export default function Admin() {
  const [users, setUsers] = useState<User[]>([]);
  const [error, setError] = useState<string | null>(null);
  const load = () => api<{ users: User[] }>("/admin/users").then((r) => setUsers(r.users)).catch((e: ApiError) => setError(e.message));
  useEffect(() => { load(); }, []);

  const change = async (u: User, role: string, add: boolean) => {
    try {
      if (add) await api(`/admin/users/${u.id}/roles`, { method: "POST", body: JSON.stringify({ role }) });
      else await api(`/admin/users/${u.id}/roles/${role}`, { method: "DELETE" });
      load();
    } catch (e) {
      setError((e as ApiError).message);
    }
  };

  return (
    <>
      <h1>Users</h1>
      {error && <p className="error">{error}</p>}
      <table>
        <thead><tr><th>Name</th><th>Email</th><th>Roles</th><th /></tr></thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.id}>
              <td>{u.name}</td><td>{u.email}</td><td>{u.roles.join(", ")}</td>
              <td>
                {["admin", "support"].map((r) => (
                  <button key={r} onClick={() => change(u, r, !u.roles.includes(r))} style={{ marginRight: 6 }}>
                    {u.roles.includes(r) ? `Remove ${r}` : `Make ${r}`}
                  </button>
                ))}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
}
