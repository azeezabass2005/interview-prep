import "./globals.css";
import type { ReactNode } from "react";

export const metadata = { title: "Market Data API" };

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="topbar">
          <a href="/">Market Data API</a>
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}
