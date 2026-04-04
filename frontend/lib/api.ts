const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000'

export type Submission = {
  id: number
  source_type: 'FILE' | 'URL'
  filename: string
  target_url?: string | null
  sha256?: string | null
  status: string
  created_at: string
}

export async function createFileSubmission(formData: FormData) {
  const res = await fetch(`${API_BASE}/api/v1/submissions/file/upload`, {
    method: 'POST',
    body: formData
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function createUrlSubmission(url: string) {
  const res = await fetch(`${API_BASE}/api/v1/submissions/url`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url })
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function getSubmission(id: string) {
  const res = await fetch(`${API_BASE}/api/v1/submissions/${id}`, { cache: 'no-store' })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export async function getReport(id: string) {
  const res = await fetch(`${API_BASE}/api/v1/submissions/${id}/report`, { cache: 'no-store' })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}
