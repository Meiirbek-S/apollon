import { JsonBlock } from '@/components/JsonBlock'

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
  const value = indicator.toLowerCase()
  if (value.includes('createprocess') || value.includes('winexec') || value.includes('shellexecute')) {
    return 'Файл использует функции запуска других процессов.'
  }
  if (value.includes('loadlibrary') || value.includes('getprocaddress')) {
    return 'Файл динамически загружает системные библиотеки.'
  }
  if (value.includes('virtualalloc') || value.includes('writememory') || value.includes('createremotethread')) {
    return 'Обнаружены признаки внедрения кода в память.'
  }
  if (value.includes('powershell') || value.includes('cmd.exe')) {
    return 'Файл может запускать скриптовые или консольные команды.'
  }
  if (value.includes('packed') || value.includes('entropy')) {
    return 'Структура файла выглядит обфусцированной или упакованной.'
  }
  if (value.includes('network') || value.includes('socket') || value.includes('http')) {
    return 'Файл содержит признаки сетевой активности.'
  }
  return indicator
}

function getTopReasons(report: FileReport): string[] {
  const raw = [...(report.risk_indicators || []), ...(report.suspicious_imports || [])]
  const mapped = raw.map(humanizeIndicator)
  const unique = Array.from(new Set(mapped))
  return unique.slice(0, 6)
}

export function FileReportView({ report }: { report: FileReport }) {
  const verdict = normalizeVerdict(report)
  const reasons = getTopReasons(report)

  return (
    <section className="card file-report">
      <div className={`verdict-banner ${verdictClass(verdict)}`}>
        <div>
          <p className="muted">File security verdict</p>
          <h2>{verdict}</h2>
          <p className="verdict-text">{report.verdict_reason || meaningText(verdict)}</p>
        </div>
        <div className="score-box">
          <span>Risk score</span>
          <strong>{report.risk_score ?? 0}</strong>
          <small>Risk level: {report.risk_level || verdict}</small>
        </div>
      </div>

      <div className="overview-grid">
        <div className="overview-card"><span>File name</span><strong>{report.original_filename || '-'}</strong></div>
        <div className="overview-card"><span>File type</span><strong>{report.mime_type || '-'}</strong></div>
        <div className="overview-card"><span>Size</span><strong>{formatBytes(report.file_size)}</strong></div>
        <div className="overview-card"><span>Hash</span><strong>{shortenHash(report.sha256)}</strong></div>
        <div className="overview-card"><span>PE format</span><strong>{report.is_pe ? 'Yes' : 'No'}</strong></div>
        <div className="overview-card"><span>Compile time</span><strong>{report.compile_timestamp || '-'}</strong></div>
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
        <h3>Risk indicators</h3>
        <div className="chips">
          {(report.risk_indicators || []).length > 0 ? (
            report.risk_indicators?.map((item) => (
              <span className="chip chip-risk" key={item}>
                {humanizeIndicator(item)}
              </span>
            ))
          ) : (
            <span className="muted">No explicit risk indicators found.</span>
          )}
        </div>
      </div>

      {report.is_pe && (
        <div className="card soft">
          <h3>PE details</h3>
          <div className="overview-grid compact">
            <div className="overview-card"><span>Machine type</span><strong>{report.machine_type || '-'}</strong></div>
            <div className="overview-card"><span>Entry point</span><strong>{report.entry_point || '-'}</strong></div>
            <div className="overview-card"><span>Image base</span><strong>{report.image_base || '-'}</strong></div>
            <div className="overview-card"><span>Suspicious imports</span><strong>{(report.suspicious_imports || []).length}</strong></div>
          </div>
        </div>
      )}

      <div className="card soft">
        <h3>What this means</h3>
        <p>{meaningText(verdict)}</p>
      </div>

      <details className="card soft">
        <summary>Technical details</summary>
        <div className="tech-grid">
          <p><b>full sha256:</b> {report.sha256 || '-'}</p>
          <p><b>mime type:</b> {report.mime_type || '-'}</p>
          <p><b>extension:</b> {report.extension || '-'}</p>
          <p><b>is_pe:</b> {String(report.is_pe)}</p>
          <p><b>machine_type:</b> {report.machine_type || '-'}</p>
          <p><b>entry_point:</b> {report.entry_point || '-'}</p>
          <p><b>image_base:</b> {report.image_base || '-'}</p>
          <p><b>compile_timestamp:</b> {report.compile_timestamp || '-'}</p>
        </div>

        <h4>Suspicious imports</h4>
        <JsonBlock data={report.suspicious_imports || []} />
        <h4>Imported functions</h4>
        <JsonBlock data={report.imported_functions || []} />
        <h4>PE sections</h4>
        <JsonBlock data={report.pe_sections || []} />
      </details>

      <details className="card soft">
        <summary>Show full technical report (raw JSON)</summary>
        <JsonBlock data={report} />
      </details>
    </section>
  )
}
