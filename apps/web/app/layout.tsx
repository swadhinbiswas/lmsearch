import type { Metadata } from "next";
import { ThemeToggle } from "@/components/theme-toggle";
import "./globals.css";

export const metadata: Metadata = { title: "lmsearch", description: "AI natural-language product search" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-screen antialiased">
        <a href="#main" className="sr-only focus:not-sr-only">Skip to content</a>
        <header className="border-b">
          <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
            <span className="font-bold" aria-label="lmsearch home">lmsearch</span>
            <ThemeToggle />
          </div>
        </header>
        <div id="main">{children}</div>
      </body>
    </html>
  );
}
