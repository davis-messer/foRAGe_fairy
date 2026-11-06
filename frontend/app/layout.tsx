import type { Metadata } from "next";
import { Audiowide, DotGothic16, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Audiowide({
  weight: "400",
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const pixelFont = DotGothic16({
  weight: "400",
  variable: "--font-pixel",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "foRAGe_fairy",
  description: "Chat with your documents",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable} ${pixelFont.variable}`}>
        {children}
      </body>
    </html>
  );
}
