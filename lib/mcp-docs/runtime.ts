import documents from './index.json';
import rules from './rules.json';
import { createDocumentationService, DocumentationError } from './service.mjs';
export const documentation = createDocumentationService(documents, rules);
export function errorResponse(error: unknown): Response {
  if (error instanceof DocumentationError) return Response.json({ error: error.message }, { status: error.status });
  return Response.json({ error: 'Documentation service unavailable.' }, { status: 500 });
}
