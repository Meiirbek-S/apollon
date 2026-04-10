export function JsonBlock({ data }: { data: unknown }) {
  return (
<<<<<<< HEAD
    <pre style={{ background: '#0b1020', color: '#d6e4ff', padding: 16, borderRadius: 8, overflow: 'auto' }}>
=======
    <pre className="json-block">
>>>>>>> codex/design-web-system-for-malware-analysis-5z4ma5
      {JSON.stringify(data, null, 2)}
    </pre>
  )
}
