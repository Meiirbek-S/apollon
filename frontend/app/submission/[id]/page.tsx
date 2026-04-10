import Link from 'next/link'
import { getSubmission } from '@/lib/api'

export default async function SubmissionPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const submission = await getSubmission(id)

  return (
    <div className="card">
      <h2>Submission #{id}</h2>
<<<<<<< HEAD
      <p><b>submission_id:</b> {submission.id}</p>
      <p><b>status:</b> {submission.status}</p>
      <p><b>source_type:</b> {submission.source_type}</p>
      <p><b>filename:</b> {submission.filename}</p>
      <p><b>target_url:</b> {submission.target_url ?? '-'}</p>
      <p><b>sha256:</b> {submission.sha256 ?? '-'}</p>
      <p><b>created_at:</b> {submission.created_at}</p>
      <div className="row">
=======
      <div className="overview-grid compact">
        <div className="overview-card"><span>Submission ID</span><strong>{submission.id}</strong></div>
        <div className="overview-card"><span>Status</span><strong>{submission.status}</strong></div>
        <div className="overview-card"><span>Source type</span><strong>{submission.source_type}</strong></div>
        <div className="overview-card"><span>Filename / URL</span><strong>{submission.filename}</strong></div>
        <div className="overview-card"><span>target_url</span><strong>{submission.target_url ?? '-'}</strong></div>
        <div className="overview-card"><span>sha256</span><strong>{submission.sha256 ?? '-'}</strong></div>
      </div>
      <p className="muted">created_at: {submission.created_at}</p>
      <div className="row action-row">
>>>>>>> codex/design-web-system-for-malware-analysis-5z4ma5
        <Link href={`/report/${id}`}>Open Report</Link>
      </div>
    </div>
  )
}
