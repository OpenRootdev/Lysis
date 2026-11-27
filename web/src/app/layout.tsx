import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { SITE_URL } from "@/lib/site";
import { Analytics } from "@vercel/analytics/next";

const geistSans = Geist({
  variable: "--font-geist-sans",
  
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const title = "Lysis: Find Good First Issues on GitHub for Beginners";
const description =
  "Find good first issues on GitHub you can actually finish. Lysis ranks a repo's open issues by how likely a first-time contributor is to get a PR merged.";
  
export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: { default: title, template: "%s | Lysis" },
  description,
  alternates: { canonical: "/" },
  openGraph: { type: "website", siteName: "Lysis", url: "/", title, description },
  twitter: { card: "summary_large_image", title, description },
};


const jsonLd = JSON.stringify({
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "WebSite",
      "@id": `${SITE_URL}/#website`,
      name: "Lysis",
      alternateName: ["Lysis", "trylysis.me"],
      url: `${SITE_URL}/`,
    },
    {
      "@type": "WebApplication",
      name: "Lysis",
      url: `${SITE_URL}/`,
      description,
      applicationCategory: "DeveloperApplication",
      operatingSystem: "Any",
      offers: { "@type": "Offer", price: "0", priceCurrency: "USD" },
    },
  ],
}).replace(/</g, "\\u003c");


export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: jsonLd }} />
        {children}
        <Analytics />
      </body>
    </html>
  );
}
