export default async function handler(req, res) {
  const body = req.body;
  const BACKEND = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8080';
  try {
    const response = await fetch(`${BACKEND}/process`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    const data = await response.json();
    res.status(response.status).json(data);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
}
