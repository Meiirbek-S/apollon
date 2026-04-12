'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

const navItems = [
  { href: '/', label: 'Overview' },
  { href: '/upload-file', label: 'Upload File' },
  { href: '/analyze-url', label: 'Analyze URL' },
]

export function AppNav() {
  const pathname = usePathname()

  return (
    <nav className="nav-shell" aria-label="Main navigation">
      {navItems.map((item) => {
        const active = pathname === item.href
        return (
          <Link
            key={item.href}
            href={item.href}
            className={`nav-link ${active ? 'active' : ''}`}
          >
            {item.label}
          </Link>
        )
      })}
    </nav>
  )
}
