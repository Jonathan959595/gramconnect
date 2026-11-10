import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = { title: "GRAMCONNECT | Village civic assistance", description: "Village civic assistance and case management" };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
