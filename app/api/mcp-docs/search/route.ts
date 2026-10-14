import { documentation, errorResponse } from '@/lib/mcp-docs/runtime';
export function GET(request: Request) {
  try {
    const params = new URL(request.url).searchParams;
    return Response.json(documentation.search({ q: params.get('q'), sku: params.get('sku') ?? undefined, limit: params.get('limit') ?? undefined }));
  } catch (error) { return errorResponse(error); }
}
