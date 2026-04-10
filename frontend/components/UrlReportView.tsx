import { JsonBlock } from '@/components/JsonBlock'

type UrlReport = {
  normalized_url: string
  final_url?: string | null
  domain: string
  hostname?: string
  scheme?: string
  path?: string
  query_present?: boolean
  port?: number | null
  resolved_ip?: string | null
  dns_resolved?: boolean
  uses_https?: boolean
  redirect_count?: number
  risk_score?: number
  risk_level: 'SAFE' | 'SUSPICIOUS' | 'MALWARE-LIKE' | string
  risk_indicators?: string[]
  verdict_reason?: string
  analyzed_at?: string
  created_at?: string
}

function verdictRu(level: string) {
  if (level === 'SAFE') return 'БЕЗОПАСНО'
  if (level === 'SUSPICIOUS') return 'ПОДОЗРИТЕЛЬНО'
  return 'ОПАСНО'
}

function verdictClass(level: string) {
  if (level === 'SAFE') return 'verdict-safe'
  if (level === 'SUSPICIOUS') return 'verdict-suspicious'
  return 'verdict-malware'
}

function whatMeans(level: string) {
  if (level === 'SAFE') return 'Ссылка не показывает выраженных опасных признаков на текущем этапе проверки.'
  if (level === 'SUSPICIOUS') return 'Ссылка содержит риск-сигналы. Открывайте с осторожностью и лучше в изолированной среде.'
  return 'Ссылка выглядит опасной. Не рекомендуется открывать её на рабочем устройстве.'
}

export function UrlReportView({ report }: { report: UrlReport }) {
  const indicators = report.risk_indicators || []
  const reasons = indicators.slice(0, 6)

  return (
    <section className="card file-report">
      <div className={`verdict-banner ${verdictClass(report.risk_level)}`}>
        <div>
          <p className="muted">Оценка безопасности URL</p>
          <h2>{verdictRu(report.risk_level)}</h2>
          <p className="verdict-text">{report.verdict_reason || whatMeans(report.risk_level)}</p>
        </div>
        <div className="score-box">
          <span>Уровень риска (баллы)</span>
          <strong>{report.risk_score ?? 0}</strong>
          <small>Уровень угрозы: {report.risk_level}</small>
        </div>
      </div>

      <div className="overview-grid">
        <div className="overview-card"><span>URL</span><strong>{report.normalized_url}</strong></div>
        <div className="overview-card"><span>Хост</span><strong>{report.hostname || report.domain}</strong></div>
        <div className="overview-card"><span>HTTPS</span><strong>{report.uses_https ? 'Да' : 'Нет'}</strong></div>
        <div className="overview-card"><span>DNS резолв</span><strong>{report.dns_resolved ? 'Успешно' : 'Не удалось'}</strong></div>
        <div className="overview-card"><span>IP</span><strong>{report.resolved_ip || '-'}</strong></div>
        <div className="overview-card"><span>Порт</span><strong>{report.port ?? (report.uses_https ? 443 : 80)}</strong></div>
      </div>

      <div className="card soft">
        <h3>Почему такой результат</h3>
        {reasons.length > 0 ? (
          <ul className="plain-list">
            {reasons.map((reason) => (<li key={reason}>{reason}</li>))}
          </ul>
        ) : (
          <p className="muted">Явные признаки риска не обнаружены.</p>
        )}
      </div>

      <div className="card soft">
        <h3>Признаки риска</h3>
        <div className="chips">
          {indicators.length > 0 ? (
            indicators.map((item) => <span className="chip chip-risk" key={item}>{item}</span>)
          ) : (
            <span className="muted">Сигналы риска отсутствуют.</span>
          )}
        </div>
      </div>

      <div className="card soft">
        <h3>Что это означает</h3>
        <p>{whatMeans(report.risk_level)}</p>
      </div>

      <details className="card soft">
        <summary>Технические детали URL-анализа</summary>
        <div className="tech-grid">
          <p><b>normalized_url:</b> {report.normalized_url}</p>
          <p><b>final_url:</b> {report.final_url || report.normalized_url}</p>
          <p><b>scheme:</b> {report.scheme || '-'}</p>
          <p><b>hostname:</b> {report.hostname || report.domain}</p>
          <p><b>path:</b> {report.path || '/'}</p>
          <p><b>query_present:</b> {String(report.query_present)}</p>
          <p><b>redirect_count:</b> {report.redirect_count ?? 0}</p>
          <p><b>dns_resolved:</b> {String(report.dns_resolved)}</p>
          <p><b>resolved_ip:</b> {report.resolved_ip || '-'}</p>
          <p><b>risk_score:</b> {report.risk_score ?? 0}</p>
          <p><b>risk_level:</b> {report.risk_level}</p>
          <p><b>analyzed_at:</b> {report.analyzed_at || '-'}</p>
          <p><b>created_at:</b> {report.created_at || '-'}</p>
        </div>
      </details>

      <details className="card soft">
        <summary>Сырой URL-отчет (JSON)</summary>
        <JsonBlock data={report} />
      </details>
    </section>
  )
}
