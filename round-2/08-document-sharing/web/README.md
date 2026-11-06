# Web app

The Next.js front end for this service. It talks to the Python API through the `/api/*` rewrite in `next.config.mjs`.

```bash
python server.py           # in the repository root: the API on :8000
cd web && npm install && npm run dev   # the web app on :3000
```

Paste a token from `python -m vault.seed` into the login box (it's stored in localStorage).
The tickets in this repository are backend issues; you shouldn't need to change anything here.
