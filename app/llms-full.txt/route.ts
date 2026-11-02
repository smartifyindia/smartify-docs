import { markdownPage, publicDocPages } from '@/lib/agent-docs';

export const dynamic = 'force-static';

export async function GET() {
  const pages = await Promise.all(publicDocPages().map(markdownPage));
  return new Response(pages.join('\n\n---\n\n'), {
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
  });
}
