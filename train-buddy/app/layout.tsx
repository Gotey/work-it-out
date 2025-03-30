import type React from "react";
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/theme-provider";
import Navigation from "@/components/navigation";
import Footer from "@/components/footer";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Train Buddy",
  description: "Your personal workout companion",
  generator: "v0.dev",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider
          attribute="class"
          defaultTheme="light"
          enableSystem
          disableTransitionOnChange
        >
          <div className="flex min-h-screen flex-col">
            {/* ✅ TOP PARTITION */}
            <div className="bg-[hsl(var(--header))] shadow-inner">
              <Navigation />
            </div>

            {/* ✅ MIDDLE PARTITION */}
            <div className="flex-1 bg-[hsl(var(--content))]">{children}</div>

            {/* ✅ BOTTOM PARTITION */}
            <div className="bg-[hsl(var(--footer))] text-white shadow-inner">
              <Footer />
            </div>
          </div>
        </ThemeProvider>
      </body>
    </html>
  );
}
