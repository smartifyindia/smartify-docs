import type { ReactNode } from 'react';
import { DocsLayout } from 'fumadocs-ui/layouts/docs';
import { source } from '@/lib/source';
import Image from 'next/image';
import { LayoutGrid, Cable, Zap } from 'lucide-react';

function TabIcon({ children, bg }: { children: ReactNode; bg: string }) {
  return (
    <div
      className="flex size-9 md:size-5 items-center justify-center rounded-lg shadow-sm ring-1 ring-black/5 dark:ring-white/10"
      style={{ background: bg }}
    >
      {children}
    </div>
  );
}

const tabIcons: Record<string, ReactNode> = {
  Products: (
    <TabIcon bg="linear-gradient(135deg, #0FABBB 0%, #0d8f9e 100%)">
      <LayoutGrid className="size-5 md:size-3 text-white" />
    </TabIcon>
  ),
  'Installation Guides': (
    <TabIcon bg="linear-gradient(135deg, #f59e0b 0%, #d97706 100%)">
      <Cable className="size-5 md:size-3 text-white" />
    </TabIcon>
  ),
  'Smartify Pro': (
    <TabIcon bg="linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)">
      <Zap className="size-5 md:size-3 text-white" />
    </TabIcon>
  ),
};

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <DocsLayout
      tree={source.pageTree}
      nav={{
        title: (
          <span className="flex items-center gap-2">
            <Image
              src="/logo.png"
              alt="Smartify"
              width={178}
              height={48}
              className="h-8 w-auto dark:[filter:brightness(0)_invert(1)]"
            />
          </span>
        ),
        url: '/docs',
      }}
      sidebar={{
        tabs: {
          transform: (option, node) => ({
            ...option,
            icon: tabIcons[String(node.name)] ?? option.icon,
          }),
        },
      }}
    >
      {children}
    </DocsLayout>
  );
}
