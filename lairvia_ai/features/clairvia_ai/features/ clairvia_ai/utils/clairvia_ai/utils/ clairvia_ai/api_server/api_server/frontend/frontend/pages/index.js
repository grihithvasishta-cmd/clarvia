import { useState } from 'react';

export default function Home() {
  const [url, setUrl] = useState('');
  const [source, setSource] = useState('pdf');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    try {
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || '/api';
      const res = await fetch(`${apiBase}/process`, {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ source_type: source, path_or_url: url })
      });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setResult({ error: err.message });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ padding: 24, fontFamily: 'Arial, sans-serif' }}>
      <h1>Clairvia AI - Demo Frontend</h1>
      <form onSubmit={handleSubmit} style={{ marginBottom: 20 }}>
        <label>
          Source Type:
          <select value={source} onChange={(e) => setSource(e.target.value)} style={{ marginLeft: 8 }}>
            <option value="pdf">PDF (path or URL)</option>
            <option value="audio">Audio (path or URL)</option>
            <option value="youtube">YouTube URL</option>
            <option value="image">Image (path or URL)</option>
          </select>
        </label>
        <br /><br />
        <label>
          Path or URL:
          <input value={url} onChange={(e) => setUrl(e.target.value)} style={{ marginLeft: 8, width: 400 }} />
        </label>
        <br /><br />
        <button type="submit" disabled={loading}>{loading ? 'Processing...' : 'Process'}</button>
      </form>

      <pre style={{ whiteSpace: 'pre-wrap', background: '#f6f6f6', padding: 12 }}>
        {result ? JSON.stringify(result, null, 2) : 'No result yet.'}
      </pre>
    </div>
  );
}
