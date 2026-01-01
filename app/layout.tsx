import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'CoffeeCompass - Discover Your Perfect Coffee Shop',
  description: 'Find the perfect coffee shop for studying, remote work, dates, or meetings',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh">
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}

