import type { Metadata } from "next";
import { ThemeProvider } from "next-themes";
import { Sidebar } from "@/components/sidebar";
import { MobileSidebar } from "@/components/mobile-sidebar";
import "./globals.css";

export const metadata: Metadata = {
  title: "llmbattler - AI Battle Arena",
  description: "Compare and evaluate LLM responses through blind side-by-side testing",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="antialiased">
        <ThemeProvider attribute="class" defaultTheme="dark" enableSystem={false}>
          <div className="flex h-screen overflow-hidden">
            {/* Desktop Sidebar */}
            <aside className="hidden md:block">
              <Sidebar />
            </aside>

            {/* Main Content */}
            <div className="flex flex-1 flex-col overflow-hidden">
              {/* Mobile Header */}
              <header className="flex items-center gap-4 border-b border-zinc-800 bg-zinc-950 p-4 md:hidden">
                <MobileSidebar />
                <h1 className="text-lg font-semibold text-zinc-100">LMArena</h1>
              </header>

              {/* Page Content */}
              <main className="flex-1 overflow-auto bg-zinc-900">
                {children}
              </main>
            </div>
          </div>
        </ThemeProvider>
      </body>
    </html>
  );
}
