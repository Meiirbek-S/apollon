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
  let pendingReason: string | null = null
  let unavailableReason: string | null = null
  let backendError: string | null = null

  try {
    reportResponse = await getReport(id)
  } catch (error) {
    const isMissingUrlReport =
      submission.source_type === 'URL' &&
      isApiError(error) &&
      error.status === 404 &&
      (error.detail || '').toLowerCase().includes('url analysis report not found')

    if (isMissingUrlReport) {
      try {
        const directUrlReport = await getUrlReport(id)
        reportResponse = { report_type: 'URL', report: directUrlReport }
      } catch (urlError) {
        if (isApiError(urlError) && urlError.status === 404) {
          pendingReason = 'Результат URL-анализа пока не найден.'
        } else {
          throw urlError
        }
      }
      return renderPage()
    }

    if (isApiError(error) && error.status === 404 && submission.source_type === 'FILE') {
      const detail = (error.detail || '').toLowerCase()
      if (detail.includes('not ready')) {
        pendingReason = 'Статический анализ еще выполняется.'
      } else if (detail.includes('failed')) {
        unavailableReason = 'Анализ завершился ошибкой, поэтому отчет недоступен.'
      } else {
        unavailableReason = 'Статический отчет для этого submission пока не найден.'
      }
    } else {
      if (isApiError(error)) {
        backendError = error.detail || `Backend error (${error.status})`
      } else {
        backendError = 'Не удалось загрузить отчет из backend.'
      }
    }
  }

  return renderPage()

  function renderPage() {
  const report = reportResponse?.report

  return (
    <div className="card">
      <h2>Report for submission #{id}</h2>

      <div className="card soft">
        <h3>Submission Summary</h3>
        <div className="overview-grid compact">
          <div className="overview-card"><span>Submission ID</span><strong>{submission.id}</strong></div>
          <div className="overview-card"><span>Status</span><strong>{submission.status}</strong></div>
          <div className="overview-card"><span>Source type</span><strong>{submission.source_type}</strong></div>
        </div>
      </div>

      {reportResponse?.report_type === 'FILE' && (
        <FileReportView report={report} />
      )}

      {reportResponse?.report_type === 'URL' && (
        <UrlReportView report={report} />
      )}

      {!reportResponse && submission.source_type === 'URL' && (
        <div className="card empty-state">
          <h3>Отчет еще не готов</h3>
          <p>URL-анализ выполняется или был завершен без сохраненного отчета.</p>
          <p>{pendingReason || 'Результат URL-анализа пока не найден.'}</p>
        </div>
      )}

      {!reportResponse && submission.source_type === 'FILE' && pendingReason && (
        <div className="card empty-state">
          <h3>Отчет еще не готов</h3>
          <p>{pendingReason}</p>
        </div>
      )}

      {!reportResponse && submission.source_type === 'FILE' && unavailableReason && (
        <div className="card empty-state">
          <h3>Отчет недоступен</h3>
          <p>{unavailableReason}</p>
          <p className="muted">submission status: {submission.status}</p>
        </div>
      )}

      {!reportResponse && backendError && (
        <div className="card empty-state">
          <h3>Ошибка backend</h3>
          <p>{backendError}</p>
          <p className="muted">Проверьте логи API/worker и состояние миграций БД.</p>
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
}
