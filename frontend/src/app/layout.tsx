import type { Metadata } from "next";
import "./globals.css";
import { ClientLayout } from "@/components/ClientLayout";

export const metadata: Metadata = {
  metadataBase: new URL('https://gocart.app'),
  title: {
    default: 'Go, Cart! - Favorites on repeat. New loves on deck. Groceries on autopilot.',
    template: '%s | Go, Cart!'
  },
  description: "AI-powered meal planning that feels like making a playlist. Save recipes from anywhere, drag-and-drop meal plans, and get smart grocery lists with zero duplicates. One tap to your cart.",
  keywords: [
    'meal planning',
    'grocery list',
    'recipe organizer',
    'meal prep',
    'grocery delivery',
    'smart shopping',
    'meal planner app',
    'recipe management',
    'automatic grocery list',
    'meal planning automation',
    'Go Cart',
    'Knuspr integration',
    'ingredient aggregation'
  ],
  authors: [{ name: 'Go, Cart!' }],
  creator: 'Go, Cart!',
  publisher: 'Go, Cart!',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://gocart.app',
    siteName: 'Go, Cart!',
    title: 'Go, Cart! - Favorites on repeat. New loves on deck. Groceries on autopilot.',
    description: 'Meal planning that feels like making a playlist. Smart recipes, automatic grocery lists, zero duplicates.',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'Go, Cart! - AI-Powered Meal Planning',
        type: 'image/png',
      },
      {
        url: '/og-image-square.png',
        width: 1200,
        height: 1200,
        alt: 'Go, Cart! Logo',
        type: 'image/png',
      }
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Go, Cart! - Favorites on repeat. New loves on deck. Groceries on autopilot.',
    description: 'Meal planning that feels like making a playlist. Smart recipes, automatic grocery lists, zero duplicates.',
    creator: '@gocartapp',
    images: ['/twitter-card.png'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  icons: {
    icon: [
      { url: '/favicon-16x16.png', sizes: '16x16', type: 'image/png' },
      { url: '/favicon-32x32.png', sizes: '32x32', type: 'image/png' },
    ],
    apple: [
      { url: '/apple-touch-icon.png', sizes: '180x180', type: 'image/png' },
    ],
    other: [
      { url: '/android-chrome-192x192.png', rel: 'icon', sizes: '192x192', type: 'image/png' },
      { url: '/android-chrome-512x512.png', rel: 'icon', sizes: '512x512', type: 'image/png' },
    ],
  },
  manifest: '/site.webmanifest',
  category: 'food',
};

export const viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
  userScalable: true,
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#FAF7F5' },
    { media: '(prefers-color-scheme: dark)', color: '#1A1A2E' }
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://api.fontshare.com/v2/css?f[]=cabinet-grotesk@400,500,700,800&display=swap" rel="stylesheet" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />

        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              '@context': 'https://schema.org',
              '@type': 'WebApplication',
              name: 'Go, Cart!',
              url: 'https://gocart.app',
              description: 'AI-powered meal planning that feels like making a playlist. Save recipes from anywhere, drag-and-drop meal plans, and get smart grocery lists with zero duplicates.',
              applicationCategory: 'LifestyleApplication',
              operatingSystem: 'Web',
              offers: {
                '@type': 'Offer',
                price: '0',
                priceCurrency: 'USD'
              },
              aggregateRating: {
                '@type': 'AggregateRating',
                ratingValue: '4.8',
                ratingCount: '1250'
              },
              featureList: [
                'Recipe organization from any source',
                'Drag-and-drop meal planning',
                'Smart ingredient aggregation',
                'Automatic grocery list generation',
                'Knuspr grocery delivery integration',
                'Nutrition tracking',
                'Dietary preference support'
              ]
            })
          }}
        />
      </head>
      <body className="antialiased font-body">
        <a href="#main-content" className="skip-to-content">
          Skip to main content
        </a>
        <ClientLayout>
          {children}
        </ClientLayout>
      </body>
    </html>
  );
}
