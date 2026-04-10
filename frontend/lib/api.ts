const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000'

<<<<<<< HEAD
=======
export class ApiError extends Error {
  status: number
  detail?: string
  payload?: unknown

  constructor(message: string, status: number, detail?: string, payload?: unknown) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.detail = detail
    this.payload = payload
  }
}

async function toApiError(res: Response): Promise<ApiError> {
  let payload: unknown = null
  let detail: string | undefined

  try {
    payload = await res.json()
    if (payload && typeof payload === 'object' && 'detail' in payload) {
      detail = String((payload as { detail?: unknown }).detail ?? '')
    }
  } catch {
    const text = await res.text()
    payload = text
    detail = text || undefined
  }

  return new ApiError(detail || `HTTP ${res.status}`, res.status, detail, payload)
}

export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError
}

>>>>>>> codex/design-web-system-for-malware-analysis-5z4ma5
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
<<<<<<< HEAD
  if (!res.ok) throw new Error(await res.text())
=======
  if (!res.ok) throw await toApiError(res)
>>>>>>> codex/design-web-system-for-malware-analysis-5z4ma5
  return res.json()
}

export async function createUrlSubmission(url: string) {
  const res = await fetch(`${API_BASE}/api/v1/submissions/url`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url })
  })
<<<<<<< HEAD
  if (!res.ok) throw new Error(await res.text())
=======
  if (!res.ok) throw await toApiError(res)
>>>>>>> codex/design-web-system-for-malware-analysis-5z4ma5
  return res.json()
}

export async function getSubmission(id: string) {
  const res = await fetch(`${API_BASE}/api/v1/submissions/${id}`, { cache: 'no-store' })
<<<<<<< HEAD
  if (!res.ok) throw new Error(await res.text())
=======
  if (!res.ok) throw await toApiError(res)
>>>>>>> codex/design-web-system-for-malware-analysis-5z4ma5
  return res.json()
}

export async function getReport(id: string) {
  const res = await fetch(`${API_BASE}/api/v1/submissions/${id}/report`, { cache: 'no-store' })
<<<<<<< HEAD
  if (!res.ok) throw new Error(await res.text())
=======
  if (!res.ok) throw await toApiError(res)
  return res.json()
}

export async function getUrlReport(id: string) {
  const res = await fetch(`${API_BASE}/api/v1/submissions/${id}/url-report`, { cache: 'no-store' })
  if (!res.ok) throw await toApiError(res)
>>>>>>> codex/design-web-system-for-malware-analysis-5z4ma5
  return res.json()
}
