import "./globals.css";
import Link from "next/link";
import type { ReactNode } from "react";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="border-b p-4">
          <nav className="mx-auto flex max-w-6xl gap-4 text-sm">
            <Link href="/">Dashboard</Link>
            <Link href="/auth/login">Login</Link>
            <Link href="/auth/register">Register</Link>
            <Link href="/settings/org">Organization</Link>
            <Link href="/settings/team">Team</Link>
            <Link href="/billing">Billing</Link>
            <Link href="/skills">Skills</Link>
            <Link href="/nodes">Nodes</Link>
            <Link href="/audit">Audit</Link>
            <Link href="/security">Security</Link>
          </nav>
        </header>
        <main className="mx-auto max-w-6xl p-6">{children}</main>
      </body>
    </html>
  );
}
