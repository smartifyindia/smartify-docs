import type { ReactNode } from 'react';
import { DocsLayout } from 'fumadocs-ui/layouts/docs';
import { source } from '@/lib/source';

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <DocsLayout
      tree={source.pageTree}
      nav={{
        title: (
          <span className="flex items-center gap-2 font-semibold text-[#0FABBB]">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
              <path
                d="M10 2L3 7v11h5v-6h4v6h5V7L10 2z"
                fill="#0FABBB"
                stroke="#0FABBB"
                strokeWidth="0.5"
              />
            </svg>
            Smartify Docs
          </span>
        ),
        url: '/docs',
      }}
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
