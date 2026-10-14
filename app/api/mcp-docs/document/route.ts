import { documentation, errorResponse } from '@/lib/mcp-docs/runtime';
export function GET(request: Request) {
  try { return Response.json(documentation.document(new URL(request.url).searchParams.get('id'))); }
  catch (error) { return errorResponse(error); }
}
