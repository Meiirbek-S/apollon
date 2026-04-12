import { JsonBlock } from '@/components/JsonBlock'
import { humanizeIndicatorRu, verdictToRu } from '@/utils/fileReportRu'

type FileReport = {
  original_filename?: string | null
  sha256?: string | null
  mime_type?: string | null
  extension?: string | null
  file_size?: number | null
  risk_score?: number | null
  risk_level?: string | null
  verdict_reason?: string | null
  risk_indicators?: string[] | null
  suspicious_imports?: string[] | null
  imported_functions?: string[] | null
  pe_sections?: unknown[] | null
  is_pe?: boolean | null
  machine_type?: string | null
  compile_timestamp?: string | null
  entry_point?: string | null
  image_base?: string | null
}

function normalizeVerdict(report: FileReport): 'SAFE' | 'SUSPICIOUS' | 'MALWARE-LIKE' {
  const level = (report.risk_level || '').toUpperCase()
  if (level.includes('MALWARE') || level.includes('HIGH')) return 'MALWARE-LIKE'
  if (level.includes('SUSPICIOUS') || level.includes('MEDIUM')) return 'SUSPICIOUS'
  if ((report.risk_score ?? 0) >= 80) return 'MALWARE-LIKE'
  if ((report.risk_score ?? 0) >= 35) return 'SUSPICIOUS'
  return 'SAFE'
}

function verdictClass(verdict: 'SAFE' | 'SUSPICIOUS' | 'MALWARE-LIKE') {
  if (verdict === 'SAFE') return 'verdict-safe'
  if (verdict === 'SUSPICIOUS') return 'verdict-suspicious'
  return 'verdict-malware'
}

function meaningText(verdict: 'SAFE' | 'SUSPICIOUS' | 'MALWARE-LIKE') {
  if (verdict === 'SAFE') {
    return 'На текущем этапе файл не содержит выраженных подозрительных признаков.'
  }
  if (verdict === 'SUSPICIOUS') {
    return 'Файл содержит признаки, которые требуют осторожности и дополнительной проверки.'
  }
  return 'Файл выглядит опасным и не рекомендуется к запуску.'
}

function shortenHash(hash?: string | null): string {
  if (!hash) return '-'
  if (hash.length < 16) return hash
  return `${hash.slice(0, 12)}...${hash.slice(-8)}`
}

function formatBytes(value?: number | null) {
  if (!value || Number.isNaN(value)) return '-'
  if (value < 1024) return `${value} B`
  const kb = value / 1024
  if (kb < 1024) return `${kb.toFixed(1)} KB`
  const mb = kb / 1024
  return `${mb.toFixed(2)} MB`
}

function humanizeIndicator(indicator: string): string {
  return humanizeIndicatorRu(indicator)
}

function getTopReasons(report: FileReport): string[] {
  const raw = [...(report.risk_indicators || []), ...(report.suspicious_imports || [])]
  const mapped = raw.map(humanizeIndicator)
  const unique = Array.from(new Set(mapped))
  return unique.slice(0, 6)
}

type DynamicReport = {
  provider?: string
  sandbox_id?: string | null
  risk_score?: number
  risk_level?: string
  suspicious_actions?: string[]
  verdict_reason?: string
}

export function FileReportView({
  report,
  dynamicStatus,
  dynamicReport,
}: {
  report: FileReport
  dynamicStatus?: string
  dynamicReport?: DynamicReport | null
}) {
  const verdict = normalizeVerdict(report)
  const reasons = getTopReasons(report)

  return (
    <section className="card file-report">
      <div className={`verdict-banner ${verdictClass(verdict)}`}>
        <div>
          <p className="muted">Оценка безопасности файла</p>
          <h2>{verdictToRu(verdict)}</h2>
          <p className="verdict-text">{report.verdict_reason || meaningText(verdict)}</p>
        </div>
        <div className="score-box">
          <span>Уровень риска (баллы)</span>
          <strong>{report.risk_score ?? 0}</strong>
          <small>Уровень угрозы: {report.risk_level || verdictToRu(verdict)}</small>
        </div>
      </div>

      <div className="overview-grid">
        <div className="overview-card"><span>Имя файла</span><strong>{report.original_filename || '-'}</strong></div>
        <div className="overview-card"><span>Тип файла</span><strong>{report.mime_type || '-'}</strong></div>
        <div className="overview-card"><span>Размер</span><strong>{formatBytes(report.file_size)}</strong></div>
        <div className="overview-card"><span>Хэш</span><strong>{shortenHash(report.sha256)}</strong></div>
        <div className="overview-card"><span>PE-формат</span><strong>{report.is_pe ? 'Да' : 'Нет'}</strong></div>
        <div className="overview-card"><span>Дата компиляции</span><strong>{report.compile_timestamp || '-'}</strong></div>
      </div>

      <div className="card soft">
        <h3>Почему такой результат</h3>
        {reasons.length > 0 ? (
          <ul className="plain-list">
            {reasons.slice(0, 6).map((reason) => (
              <li key={reason}>{reason}</li>
            ))}
          </ul>
        ) : (
          <p className="muted">Явных подозрительных сигналов обнаружено мало или они не выражены.</p>
        )}
      </div>

      <div className="card soft">
        <h3>Признаки риска</h3>
        <div className="chips">
          {(report.risk_indicators || []).length > 0 ? (
            report.risk_indicators?.map((item) => (
              <span className="chip chip-risk" key={item}>
                {humanizeIndicator(item)}
              </span>
            ))
          ) : (
            <span className="muted">Явные признаки риска не обнаружены.</span>
          )}
        </div>
      </div>

      {report.is_pe && (
        <div className="card soft">
          <h3>Детали PE</h3>
          <div className="overview-grid compact">
            <div className="overview-card"><span>Machine type</span><strong>{report.machine_type || '-'}</strong></div>
            <div className="overview-card"><span>Точка входа</span><strong>{report.entry_point || '-'}</strong></div>
            <div className="overview-card"><span>Базовый адрес</span><strong>{report.image_base || '-'}</strong></div>
            <div className="overview-card"><span>Подозрительные импорты</span><strong>{(report.suspicious_imports || []).length}</strong></div>
          </div>
        </div>
      )}



      <div className="card soft">
        <h3>Динамический анализ</h3>
        <p><b>Статус:</b> {dynamicStatus || 'NOT_REQUESTED'}</p>
        {dynamicReport ? (
          <>
            <p><b>Провайдер:</b> {dynamicReport.provider || '-'}</p>
            <p><b>Вердикт:</b> {dynamicReport.verdict_reason || '-'}</p>
            <p><b>Risk score:</b> {dynamicReport.risk_score ?? 0}</p>
            <div className="chips">
              {(dynamicReport.suspicious_actions || []).length > 0 ? (
                dynamicReport.suspicious_actions?.map((item) => (
                  <span className="chip chip-risk" key={item}>{item}</span>
                ))
              ) : (
                <span className="muted">Подозрительные действия не обнаружены.</span>
              )}
            </div>
          </>
        ) : dynamicStatus === 'RUNNING' || dynamicStatus === 'QUEUED' ? (
          <p className="muted">Динамический анализ выполняется. Обновите страницу чуть позже.</p>
        ) : dynamicStatus === 'FAILED' ? (
          <p className="muted">Не удалось выполнить динамический анализ для этого файла.</p>
        ) : (
          <p className="muted">Динамический отчет пока недоступен или не был запрошен.</p>
        )}
      </div>
      <div className="card soft">
        <h3>Что это значит</h3>
        <p>{meaningText(verdict)}</p>
      </div>

      <details className="card soft">
        <summary>Технические детали</summary>
        <div className="tech-grid">
          <p><b>full sha256:</b> {report.sha256 || '-'}</p>
          <p><b>mime type:</b> {report.mime_type || '-'}</p>
          <p><b>extension:</b> {report.extension || '-'}</p>
          <p><b>is_pe:</b> {String(report.is_pe)}</p>
          <p><b>machine_type:</b> {report.machine_type || '-'}</p>
          <p><b>entry_point (точка входа):</b> {report.entry_point || '-'}</p>
          <p><b>image_base (базовый адрес):</b> {report.image_base || '-'}</p>
          <p><b>compile_timestamp:</b> {report.compile_timestamp || '-'}</p>
        </div>

        <h4>Подозрительные импорты (suspicious imports)</h4>
        <JsonBlock data={report.suspicious_imports || []} />
        <h4>Импортированные функции (imported functions)</h4>
        <JsonBlock data={report.imported_functions || []} />
        <h4>PE-секции (PE sections)</h4>
        <JsonBlock data={report.pe_sections || []} />
      </details>

      <details className="card soft">
        <summary>Показать полный технический отчет (raw JSON)</summary>
        <JsonBlock data={report} />
      </details>
    </section>
  )
}
