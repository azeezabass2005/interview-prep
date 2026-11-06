import "./globals.css";
import type { ReactNode } from "react";

export const metadata = { title: "Accounts" };

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="topbar">
          <a href="/">Accounts</a>
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}
