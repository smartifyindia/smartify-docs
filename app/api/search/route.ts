import { source } from '@/lib/source';
import { createSearchAPI } from 'fumadocs-core/search/server';
import type { StructuredData } from 'fumadocs-core/mdx-plugins';

export const { GET } = createSearchAPI('advanced', {
  indexes: source.getPages().map((page) => {
    const data = page.data as unknown as {
      title: string;
      description?: string;
      structuredData: StructuredData;
    };
    return {
      title: data.title,
      description: data.description ?? '',
      url: page.url,
      id: page.url,
      structuredData: data.structuredData,
    };
  }),
});
