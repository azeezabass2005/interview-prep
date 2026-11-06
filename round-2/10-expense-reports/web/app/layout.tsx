import "./globals.css";
import type { ReactNode } from "react";

export const metadata = { title: "Expenses" };

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="topbar">
          <a href="/">Expenses</a>
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}
