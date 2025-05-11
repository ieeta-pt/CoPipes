import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "@/styles/globals.css";
import { Header } from "@/components/layout/Header";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Workflow Creator",
  description: "A collaborative platform for ETL processes and data analysis.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <Header />
        {/* <div className="p-4 mx-auto max-w-(--breakpoint-2xl) md:p-6">{children}</div> */}
        {children}
      </body>
    </html>
  );
}
