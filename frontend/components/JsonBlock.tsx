export function JsonBlock({ data }: { data: unknown }) {
  return (
    <pre style={{ background: '#0b1020', color: '#d6e4ff', padding: 16, borderRadius: 8, overflow: 'auto' }}>
      {JSON.stringify(data, null, 2)}
    </pre>
  )
}
