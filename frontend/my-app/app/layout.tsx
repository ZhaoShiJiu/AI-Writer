import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "NovelWrite - AI 协同写作",
  description: "AI 协同小说续写编辑器",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN" className="h-full antialiased">
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
