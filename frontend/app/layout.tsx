import './globals.css'
import type { Metadata } from 'next'
import { AppNav } from '@/components/AppNav'

export const metadata: Metadata = {
  title: 'Apollon MVP',
  description: 'Malware analysis MVP frontend'
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="container">
          <header className="app-header">
            <div>
              <p className="eyebrow">Apollon Security</p>
              <h1>Threat Analysis MVP</h1>
              <p className="subtitle">Быстрая проверка файлов и URL с понятными отчетами по рискам.</p>
            </div>
            <AppNav />
          </header>
          {children}
        </div>
      </body>
    </html>
  )
}
