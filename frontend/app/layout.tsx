import './globals.css'
import type { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'Apollon MVP',
  description: 'Malware analysis MVP frontend'
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body suppressHydrationWarning>
        <div className="container">
          <h1>Apollon Frontend MVP</h1>
          <div className="nav">
            <Link href="/upload-file">Upload File</Link>
            <Link href="/analyze-url">Analyze URL</Link>
          </div>
          {children}
        </div>
      </body>
    </html>
  )
}
