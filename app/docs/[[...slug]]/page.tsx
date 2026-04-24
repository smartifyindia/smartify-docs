import type { Metadata } from 'next';
import type { MDXComponents } from 'mdx/types';
import React from 'react';
import { notFound } from 'next/navigation';
import { DocsPage, DocsBody, DocsDescription, DocsTitle } from 'fumadocs-ui/page';
import { getMDXComponents } from '@/mdx-components';
import { source } from '@/lib/source';

interface Props {
  params: Promise<{ slug?: string[] }>;
}

export async function generateStaticParams() {
  return source.generateParams();
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const page = source.getPage(slug);

  if (!page) return {};

  const data = page.data as unknown as { title: string; description?: string; toc: unknown; full?: boolean; body: unknown; structuredData: unknown };

  const ogUrl = new URLSearchParams({
    title: data.title,
    description: data.description ?? '',
  });

  return {
    title: data.title,
    description: data.description,
    openGraph: {
      title: data.title,
      description: data.description,
      type: 'article',
      url: `https://docs.smartify.in/docs/${slug?.join('/') ?? ''}`,
      images: [
        {
          url: `/api/og?${ogUrl.toString()}`,
          width: 1200,
          height: 630,
          alt: data.title,
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      title: data.title,
      description: data.description,
    },
    alternates: {
      canonical: `https://docs.smartify.in/docs/${slug?.join('/') ?? ''}`,
    },
  };
}

export default async function Page({ params }: Props) {
  const { slug } = await params;
  const page = source.getPage(slug);

  if (!page) notFound();

  const data = page.data as unknown as { title: string; description?: string; toc: unknown; full?: boolean; body: React.ComponentType<{ components: MDXComponents }> & ((props: { components: MDXComponents }) => React.ReactElement); structuredData: unknown };
  const MDX = data.body;

  return (
    <DocsPage
      toc={data.toc as Parameters<typeof DocsPage>[0]['toc']}
      full={data.full}
      tableOfContent={{
        style: 'clerk',
        single: false,
      }}
    >
      <DocsTitle>{data.title}</DocsTitle>
      <DocsDescription>{data.description}</DocsDescription>
      <DocsBody>
        <MDX components={getMDXComponents()} />
      </DocsBody>
    </DocsPage>
  );
}
