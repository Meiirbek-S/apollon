import { JsonBlock } from '@/components/JsonBlock'
import { FileReportView } from '@/components/FileReportView'
import { getReport, getSubmission, getUrlReport, isApiError } from '@/lib/api'

type ReportResponse = {
  report_type: 'FILE' | 'URL'
  report: any
}

export default async function ReportPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const submission = await getSubmission(id)
  let reportResponse: ReportResponse | null = null
  let urlPendingReason: string | null = null

  try {
    reportResponse = await getReport(id)
  } catch (error) {
    const isMissingUrlReport =
      submission.source_type === 'URL' &&
      isApiError(error) &&
      error.status === 404 &&
      (error.detail || '').toLowerCase().includes('url analysis report not found')

    if (!isMissingUrlReport) {
      throw error
    }

    try {
      const directUrlReport = await getUrlReport(id)
      reportResponse = { report_type: 'URL', report: directUrlReport }
    } catch (urlError) {
      if (isApiError(urlError) && urlError.status === 404) {
        urlPendingReason = 'Результат URL-анализа пока не найден.'
      } else {
        throw urlError
      }
    }
  }

  const report = reportResponse?.report

  return (
    <div className="card">
      <h2>Report for submission #{id}</h2>

      <div className="card">
        <h3>Submission Summary</h3>
        <p><b>submission id:</b> {submission.id}</p>
        <p><b>status:</b> {submission.status}</p>
        <p><b>source type:</b> {submission.source_type}</p>
      </div>

      {reportResponse?.report_type === 'FILE' && (
        <FileReportView report={report} />
      )}

      {reportResponse?.report_type === 'URL' && (
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

      {!reportResponse && submission.source_type === 'URL' && (
        <div className="card">
          <h3>Отчет еще не готов</h3>
          <p>URL-анализ выполняется или был завершен без сохраненного отчета.</p>
          <p>{urlPendingReason || 'Результат URL-анализа пока не найден.'}</p>
        </div>
      )}

      {reportResponse && (
        <>
          <h3>{reportResponse.report_type === 'FILE' ? 'Сырой отчет (JSON)' : 'Raw report payload'}</h3>
          <JsonBlock data={reportResponse} />
        </>
      )}
    </div>
  )
}
