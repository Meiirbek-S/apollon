import Link from 'next/link'
import { getSubmission } from '@/lib/api'

export default async function SubmissionPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const submission = await getSubmission(id)

  return (
    <div className="card">
      <h2>Submission #{id}</h2>
      <p><b>submission_id:</b> {submission.id}</p>
      <p><b>status:</b> {submission.status}</p>
      <p><b>source_type:</b> {submission.source_type}</p>
      <p><b>filename:</b> {submission.filename}</p>
      <p><b>target_url:</b> {submission.target_url ?? '-'}</p>
      <p><b>sha256:</b> {submission.sha256 ?? '-'}</p>
      <p><b>created_at:</b> {submission.created_at}</p>
      <div className="row">
        <Link href={`/report/${id}`}>Open Report</Link>
      </div>
    </div>
  )
}
