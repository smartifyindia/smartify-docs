import type { ReactNode } from 'react';
import { DocsLayout } from 'fumadocs-ui/layouts/docs';
import { source } from '@/lib/source';
import Image from 'next/image';

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <DocsLayout
      tree={source.pageTree}
      nav={{
        title: (
          <span className="flex items-center gap-2">
            <Image src="/logo.png" alt="Smartify" width={120} height={32} className="h-7 w-auto" />
          </span>
        ),
        url: '/docs',
      }}
      links={[{ text: 'smartify.in', url: 'https://smartify.in', external: true }]}
      sidebar={{
        banner: (
          <div className="rounded-lg border border-[#0FABBB]/20 bg-[#0FABBB]/5 px-3 py-2 text-xs text-[#0FABBB]">
            Zigbee-based smart home automation for India
          </div>
        ),
      }}
    >
      {children}
    </DocsLayout>
  );
}
