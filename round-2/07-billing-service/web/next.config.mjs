/** The browser talks to /api/*; Next proxies it to the Python service so cookies and CORS stay simple. */
const API_URL = process.env.API_URL ?? "http://localhost:8000";

export default {
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${API_URL}/:path*` }];
  },
};
