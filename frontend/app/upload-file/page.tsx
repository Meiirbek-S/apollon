'use client'

import { useState } from 'react'
import Link from 'next/link'
import { createFileSubmission } from '@/lib/api'

export default function UploadFilePage() {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!file) return

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const formData = new FormData()
      formData.append('file', file)
      const data = await createFileSubmission(formData)
      setResult(data)
    } catch (err: any) {
      setError(err.message || 'Upload failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <h2>Upload File</h2>
      <p className="muted">Загрузите файл для статического анализа и расчета risk score.</p>
      <form onSubmit={onSubmit} className="row">
        <input className="input-control" type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} />
        <button disabled={!file || loading} type="submit">
          {loading ? 'Uploading...' : 'Upload & Analyze'}
        </button>
      </form>

      {loading && <p className="state-text">Файл загружается, подождите…</p>}
      {error && <p className="error-text">{error}</p>}

      {result && (
        <div className="card success-panel">
          <h3>Submission Created</h3>
          <p><b>submission_id:</b> {result.submission_id}</p>
          <p><b>status:</b> {result.status}</p>
          <p><b>source_type:</b> FILE</p>
          <p><b>deduplicated:</b> {String(result.deduplicated)}</p>
          <div className="row action-row">
            <Link href={`/submission/${result.submission_id}`}>Open Submission</Link>
            <Link href={`/report/${result.submission_id}`}>Open Report</Link>
          </div>
        </div>
      )}
    </div>
  )
}
