import { JsonBlock } from '@/components/JsonBlock'
import { FileReportView } from '@/components/FileReportView'
import { getReport, getSubmission } from '@/lib/api'

export default async function ReportPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const submission = await getSubmission(id)
  const reportResponse = await getReport(id)
  const report = reportResponse.report

  return (
    <div className="card">
      <h2>Report for submission #{id}</h2>

      <div className="card">
        <h3>Submission Summary</h3>
        <p><b>submission id:</b> {submission.id}</p>
        <p><b>status:</b> {submission.status}</p>
        <p><b>source type:</b> {submission.source_type}</p>
      </div>

      {reportResponse.report_type === 'FILE' && (
        <FileReportView report={report} />
      )}

      {reportResponse.report_type === 'URL' && (
        <div className="card">
          <h3>URL Report</h3>
          <p><b>normalized_url:</b> {report.normalized_url}</p>
          <p><b>domain:</b> {report.domain}</p>
          <p><b>resolved_ip:</b> {report.resolved_ip ?? '-'}</p>
          <p><b>uses_https:</b> {String(report.uses_https)}</p>
          <p><b>risk_level:</b> {report.risk_level}</p>
          {report.risk_score !== undefined && <p><b>risk_score:</b> {report.risk_score}</p>}
          {report.verdict_reason && <p><b>verdict:</b> {report.verdict_reason}</p>}
          {report.risk_indicators && (
            <>
              <h4>Risk indicators</h4>
              <ul>
                {report.risk_indicators.map((v: string) => (<li key={v}>{v}</li>))}
              </ul>
            </>
          )}
        </div>
      )}

      <h3>Raw report payload</h3>
      <JsonBlock data={reportResponse} />
    </div>
  )
}
