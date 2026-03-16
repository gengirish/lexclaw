import "./globals.css";
import Link from "next/link";
import type { ReactNode } from "react";

export default function RootLayout({ children }: { children: ReactNode }) {
  const navItems = [
    { href: "/", label: "Dashboard" },
    { href: "/settings/org", label: "Organization" },
    { href: "/settings/team", label: "Team" },
    { href: "/billing", label: "Billing" },
    { href: "/skills", label: "Skills" },
    { href: "/nodes", label: "Nodes" },
    { href: "/audit", label: "Audit" },
    { href: "/security", label: "Security" },
    { href: "/auth/login", label: "Login" },
    { href: "/auth/register", label: "Register" },
  ];

  return (
    <html lang="en">
      <body>
        <header className="topbar">
          <div className="brand">
            <span className="brand-logo">LC</span>
            <div>
              <p className="brand-title">LexClaw</p>
              <p className="brand-subtitle">Legal AI Control Plane</p>
            </div>
          </div>
        </header>
        <div className="app-shell">
          <aside className="sidebar" aria-label="Main navigation">
            <nav>
              <ul className="nav-list">
                {navItems.map((item) => (
                  <li key={item.href}>
                    <Link className="nav-link" href={item.href}>
                      {item.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </nav>
          </aside>
          <main className="content">{children}</main>
        </div>
      </body>
    </html>
  );
}
