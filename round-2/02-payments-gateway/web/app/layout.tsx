import "./globals.css";
import type { ReactNode } from "react";

export const metadata = { title: "Payments Gateway" };

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="topbar">
          <a href="/">Payments Gateway</a>
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}
