import { source } from '@/lib/source';

export const docsOrigin = 'https://docs.smartify.in';

export function publicDocPages() {
  // /docs redirects to /docs/products and must not appear as a duplicate URL.
  return source.getPages().filter((page) => page.url !== '/docs')
    .sort((a, b) => a.url.localeCompare(b.url));
}

export async function markdownPage(page: ReturnType<typeof publicDocPages>[number]) {
  return `# ${page.data.title}\n\nSource: ${docsOrigin}${page.url}\n\n${await page.data.getText('processed')}`;
}
