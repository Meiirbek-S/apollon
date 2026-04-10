import Link from 'next/link'

export default function HomePage() {
  return (
<<<<<<< HEAD
    <div className="card">
      <h2>Demo UI</h2>
      <p>Choose action:</p>
      <ul>
        <li><Link href="/upload-file">Upload File for analysis</Link></li>
        <li><Link href="/analyze-url">Submit URL for analysis</Link></li>
      </ul>
    </div>
=======
    <>
      <section className="hero card">
        <h2>Анализируйте риски быстро и понятно</h2>
        <p>
          Apollon помогает оценить безопасность файла или URL, показать ключевые причины риска
          и дать прозрачный технический отчет.
        </p>
      </section>

      <section className="entry-grid">
        <article className="card entry-card">
          <h3>Загрузка файла</h3>
          <p>Проверка хэшей, базовый статический анализ и итоговый verdict с объяснением.</p>
          <Link href="/upload-file" className="btn-link">Перейти к загрузке</Link>
        </article>

        <article className="card entry-card">
          <h3>Анализ URL</h3>
          <p>Оценка URL-риска по HTTPS, DNS, структуре адреса и другим понятным эвристикам.</p>
          <Link href="/analyze-url" className="btn-link">Перейти к анализу URL</Link>
        </article>
      </section>
    </>
>>>>>>> codex/design-web-system-for-malware-analysis-5z4ma5
  )
}
