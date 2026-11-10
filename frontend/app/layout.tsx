import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = { title: "GRAMCONNECT | Civic assistance demo", description: "WhatsApp-first civic assistance prototype" };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
