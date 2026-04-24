import type { ReactNode } from 'react';
import type { Metadata } from 'next';
import { RootProvider } from 'fumadocs-ui/provider';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  metadataBase: new URL('https://docs.smartify.in'),
  title: {
    default: 'Smartify Docs — Smart Home Automation Documentation',
    template: '%s | Smartify Docs',
  },
  description:
    'Technical documentation, product specs, installation guides, and integration references for Smartify smart home automation products.',
  keywords: [
    'Smartify',
    'smart home',
    'home automation',
    'Zigbee',
    'smart switch',
    'TAC',
    'TOQ',
    'retrofit relay',
    'home assistant',
    'India',
  ],
  authors: [{ name: 'Smartify', url: 'https://smartify.in' }],
  creator: 'Smartify',
  publisher: 'Smartify',
  openGraph: {
    type: 'website',
    locale: 'en_IN',
    url: 'https://docs.smartify.in',
    siteName: 'Smartify Docs',
    title: 'Smartify Docs — Smart Home Automation Documentation',
    description:
      'Technical documentation, product specs, and installation guides for Smartify smart home automation products.',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'Smartify Docs',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Smartify Docs',
    description: 'Technical documentation for Smartify smart home automation.',
    images: ['/og-image.png'],
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
  alternates: {
    canonical: 'https://docs.smartify.in',
  },
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          rel="icon"
          href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>"
        />
      </head>
      <body className={inter.className}>
        <RootProvider>{children}</RootProvider>
      </body>
    </html>
  );
}
