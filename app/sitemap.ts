import type { MetadataRoute } from 'next';
import { docsOrigin, publicDocPages } from '@/lib/agent-docs';

export default function sitemap(): MetadataRoute.Sitemap {
  return publicDocPages().map((page) => ({ url: `${docsOrigin}${page.url}` }));
}
