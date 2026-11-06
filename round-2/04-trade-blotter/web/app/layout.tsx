import "./globals.css";
import type { ReactNode } from "react";

export const metadata = { title: "Trade Blotter" };

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="topbar">
          <a href="/">Trade Blotter</a>
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}
