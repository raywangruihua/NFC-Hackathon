import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Macro Command | NFC Hackathon MVP",
  description: "Terminal-style macroeconomics tracker frontend MVP",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
