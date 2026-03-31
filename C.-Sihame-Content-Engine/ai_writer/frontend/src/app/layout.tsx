import type { Metadata } from "next";
import { Cairo } from "next/font/google";
import "./globals.css";

const cairo = Cairo({
  subsets: ["arabic", "latin"],
  variable: "--font-cairo",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Sihame AI Content Engine",
  description: "Your strategic AI Co-Pilot",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ar" dir="rtl">
      <body className={`${cairo.variable} font-sans antialiased bg-[#FAF7F2] text-[#0D4F5C]`}>
        <main className="min-h-screen container mx-auto px-4 py-8">
          {children}
        </main>
      </body>
    </html>
  );
}
