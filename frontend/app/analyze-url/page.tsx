'use client'

import { useState } from 'react'
import Link from 'next/link'
import { createUrlSubmission } from '@/lib/api'

export default function AnalyzeUrlPage() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!url.trim()) return

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const data = await createUrlSubmission(url)
      setResult(data)
    } catch (err: any) {
      setError(err.message || 'Submit failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <h2>Analyze URL</h2>
      <form onSubmit={onSubmit} className="row">
        <input
          type="text"
          placeholder="https://example.com"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          style={{ minWidth: 420 }}
        />
        <button disabled={!url.trim() || loading} type="submit">
          {loading ? 'Submitting...' : 'Submit URL'}
        </button>
      </form>

      {error && <p style={{ color: 'crimson' }}>{error}</p>}

      {result && (
        <div className="card" style={{ marginTop: 16 }}>
          <h3>Submission Created</h3>
          <p><b>submission_id:</b> {result.submission_id}</p>
          <p><b>status:</b> {result.status}</p>
          <p><b>source_type:</b> URL</p>
          <div className="row">
            <Link href={`/submission/${result.submission_id}`}>Open Submission</Link>
            <Link href={`/report/${result.submission_id}`}>Open Report</Link>
          </div>
        </div>
      )}
    </div>
  )
}
