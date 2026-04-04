import { JsonBlock } from '@/components/JsonBlock'
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
        <div className="card">
          <h3>FILE Report</h3>
          <p><b>original filename:</b> {report.original_filename}</p>
          <p><b>sha256:</b> {report.sha256}</p>
          <p><b>mime type:</b> {report.mime_type}</p>
          <p><b>extension:</b> {report.extension}</p>
          <p><b>risk score:</b> {report.risk_score}</p>
          <p><b>risk level:</b> {report.risk_level}</p>
          <p><b>verdict reason:</b> {report.verdict_reason}</p>
          <p><b>is_pe:</b> {String(report.is_pe)}</p>
          <p><b>machine_type:</b> {report.machine_type ?? '-'}</p>
          <p><b>compile_timestamp:</b> {report.compile_timestamp ?? '-'}</p>
          <p><b>entry_point:</b> {report.entry_point ?? '-'}</p>
          <p><b>image_base:</b> {report.image_base ?? '-'}</p>

          <h4>Risk indicators</h4>
          <ul>
            {(report.risk_indicators || []).map((v: string) => (<li key={v}>{v}</li>))}
          </ul>

          <h4>Suspicious imports</h4>
          <ul>
            {(report.suspicious_imports || []).map((v: string) => (<li key={v}>{v}</li>))}
          </ul>

          <h4>PE Sections</h4>
          <JsonBlock data={report.pe_sections || []} />
        </div>
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
