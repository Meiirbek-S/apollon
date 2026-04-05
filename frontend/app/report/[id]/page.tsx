import { JsonBlock } from '@/components/JsonBlock'
import { FileReportView } from '@/components/FileReportView'
import { UrlReportView } from '@/components/UrlReportView'
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
        <UrlReportView report={report} />
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
