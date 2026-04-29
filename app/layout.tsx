import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";
import { SiteHeader } from "@/components/shared/site-header";
import { ClientProviders } from "@/components/shared/client-providers";

export const metadata: Metadata = {
  title: "klyxe lab",
  description: "interactive ai article platform"
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="klyxe-shell">
        <ClientProviders>
          <SiteHeader />
          <main>{children}</main>
        </ClientProviders>
      </body>
    </html>
  );
}
