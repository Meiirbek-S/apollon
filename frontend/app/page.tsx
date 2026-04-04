import Link from 'next/link'

export default function HomePage() {
  return (
    <div className="card">
      <h2>Demo UI</h2>
      <p>Choose action:</p>
      <ul>
        <li><Link href="/upload-file">Upload File for analysis</Link></li>
        <li><Link href="/analyze-url">Submit URL for analysis</Link></li>
      </ul>
    </div>
  )
}
