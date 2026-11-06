import "./globals.css";
import type { ReactNode } from "react";

export const metadata = { title: "Billing" };

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="topbar">
          <a href="/">Billing</a>
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}
