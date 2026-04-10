import './globals.css'
import type { Metadata } from 'next'
<<<<<<< HEAD
import Link from 'next/link'
=======
import { AppNav } from '@/components/AppNav'
>>>>>>> codex/design-web-system-for-malware-analysis-5z4ma5

export const metadata: Metadata = {
  title: 'Apollon MVP',
  description: 'Malware analysis MVP frontend'
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="container">
<<<<<<< HEAD
          <h1>Apollon Frontend MVP</h1>
          <div className="nav">
            <Link href="/upload-file">Upload File</Link>
            <Link href="/analyze-url">Analyze URL</Link>
          </div>
=======
          <header className="app-header">
            <div>
              <p className="eyebrow">Apollon Security</p>
              <h1>Threat Analysis MVP</h1>
              <p className="subtitle">Быстрая проверка файлов и URL с понятными отчетами по рискам.</p>
            </div>
            <AppNav />
          </header>
>>>>>>> codex/design-web-system-for-malware-analysis-5z4ma5
          {children}
        </div>
      </body>
    </html>
  )
}
