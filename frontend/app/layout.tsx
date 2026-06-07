import type { Metadata } from "next"
import { Barlow, Barlow_Condensed } from "next/font/google"
import "./globals.css"
import { Providers } from "./providers"

const barlow = Barlow({
  weight: ["400", "500", "600", "700"],
  subsets: ["latin"],
  variable: "--font-barlow",
})

const barlowCondensed = Barlow_Condensed({
  weight: ["400", "600", "700"],
  subsets: ["latin"],
  variable: "--font-barlow-condensed",
})

export const metadata: Metadata = {
  title: "Versigent — Safe Launch Generator",
  description: "Industrial quality management dashboard for safe launch planning",
  icons: {
    icon: [
      { url: "/favicon.ico" },
      { url: "/favicon-96x96.png", sizes: "96x96", type: "image/png" },
      { url: "/favicon.svg", type: "image/svg+xml" },
    ],
    apple: "/apple-touch-icon.png",
  },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr" suppressHydrationWarning
      className={`${barlow.variable} ${barlowCondensed.variable}`}
      style={{ fontFamily: "var(--font-barlow), system-ui, sans-serif" }}>
      <body className="min-h-screen" style={{ fontFamily: "var(--font-barlow, system-ui)" }}>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
