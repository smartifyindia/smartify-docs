import { documentation, errorResponse } from '@/lib/mcp-docs/runtime';
export async function POST(request: Request) {
  const raw = await request.text();
  if (raw.length > 10000) return Response.json({ error: 'Request too large.' }, { status: 413 });
  let body;
  try { body = JSON.parse(raw); } catch { return Response.json({ error: 'Invalid JSON.' }, { status: 400 }); }
  try { return Response.json(documentation.compatibility(body)); }
  catch (error) { return errorResponse(error); }
}
